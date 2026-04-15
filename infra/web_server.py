import json
import pulumi
import pulumi_aws as aws

import config
from container_image import ContainerImage
from monitoring import AppMonitoring
from networking import AppNetworking
from storage import AppStorage


class WebServer(pulumi.ComponentResource):
    def __init__(
        self,
        image: ContainerImage,
        storage: AppStorage,
        networking: AppNetworking,
        monitoring: AppMonitoring,
    ):
        super().__init__("meal-planner:web_server:WebServer", "meal-planner-web-server", {})

        self.role = aws.iam.Role(
            "meal-planner-web-server-role",
            name=f"{config.app_name}-web-server-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "lambda.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }],
            }),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Allows Lambda to create and manage ENIs (Elastic Network Interfaces) in the VPC.
        # Without this, Lambda can't establish a network path to VPC resources like EFS.
        aws.iam.RolePolicyAttachment(
            "meal-planner-web-server-vpc-access-policy",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole",
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Allows Lambda to mount and read/write to EFS over NFS.
        aws.iam.RolePolicyAttachment(
            "meal-planner-web-server-efs-access-policy",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonElasticFileSystemClientReadWriteAccess",
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Scoped inline policy — only allows writing logs to this function's log group.
        # CreateLogGroup is omitted because Pulumi manages the log group explicitly in
        # AppMonitoring. Granting it here would allow Lambda to create unmanaged log groups.
        # Inside .apply() the arn is a plain string, so the f-string interpolation is safe.
        aws.iam.RolePolicy(
            "meal-planner-web-server-logging-policy",
            role=self.role.name,
            policy=monitoring.log_group.arn.apply(
                lambda arn: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        "Resource": f"{arn}:*",
                    }],
                })
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.function = aws.lambda_.Function(
            "meal-planner-web-server-function",
            name=config.app_name,
            package_type="Image",
            image_uri=image.uri,
            role=self.role.arn,
            timeout=135,
            memory_size=1024,
            architectures=["x86_64"],
            vpc_config=aws.lambda_.FunctionVpcConfigArgs(
                subnet_ids=[networking.subnet.id],
                security_group_ids=[networking.web_server_security_group.id],
            ),
            # Mounts the EFS access point at mount_path inside the Lambda execution
            # environment. The access point (not the file system directly) is used here
            # because it scopes Lambda's view to /meal-planner on EFS and enforces the
            # POSIX uid/gid set in AppStorage.
            file_system_config=aws.lambda_.FunctionFileSystemConfigArgs(
                arn=storage.access_point.arn,
                local_mount_path=storage.mount_path,
            ),
            environment=aws.lambda_.FunctionEnvironmentArgs(
                variables={
                    # Four slashes: sqlite:// (scheme) + // (empty host) + /mnt/data/... (absolute path)
                    "DATABASE_URL": f"sqlite:////{storage.mount_path}/db.sqlite3",
                }
            ),
            logging_config=aws.lambda_.FunctionLoggingConfigArgs(
                log_format="Text",
                log_group=monitoring.log_group.name,
            ),
            opts=pulumi.ResourceOptions(
                parent=self,
                # The mount target must exist and be available before Lambda can
                # connect to EFS. The access_point reference above creates an implicit
                # dependency on the access point, but not on the mount target.
                depends_on=[storage.mount_target],
            ),
        )

        # Exposes the function via a public HTTPS URL. BUFFERED mode means Lambda
        # collects the full response before returning it to the caller, which is
        # required for Django (as opposed to RESPONSE_STREAM for streaming responses).
        self.function_url = aws.lambda_.FunctionUrl(
            "meal-planner-web-server-url",
            function_name=self.function.name,
            authorization_type="NONE",
            invoke_mode="BUFFERED",
            opts=pulumi.ResourceOptions(parent=self),
        )

        # The FunctionUrl resource configures *how* the URL works, but a separate
        # resource-based policy must explicitly grant public invoke access.
        # Without this permission, requests to the URL return 403.
        aws.lambda_.Permission(
            "meal-planner-web-server-public-invoke-permission",
            action="lambda:InvokeFunctionUrl",
            function=self.function.name,
            principal="*",
            function_url_auth_type="NONE",
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.url = self.function_url.function_url

        self.register_outputs({
            "function_name": self.function.name,
            "url": self.url,
        })
