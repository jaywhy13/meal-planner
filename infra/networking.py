import pulumi
import pulumi_aws as aws

import config


class AppNetworking(pulumi.ComponentResource):
    def __init__(self):
        super().__init__("meal-planner:networking:AppNetworking", "meal-planner-networking", {})

        self.vpc = aws.ec2.get_vpc(id=config.vpc_id)
        self.subnet = aws.ec2.get_subnet(id=config.subnet_id)

        # Security group attached to the Lambda function.
        # Needs outbound NFS (2049) to reach EFS, and outbound HTTPS for AWS service calls.
        self.web_server_security_group = aws.ec2.SecurityGroup(
            "meal-planner-web-server-security-group",
            name=f"{config.app_name}-web-server",
            description="Controls outbound access from the web server (Lambda)",
            vpc_id=self.vpc.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Security group attached to the EFS mount target.
        # Only accepts NFS traffic from the web server security group.
        self.storage_security_group = aws.ec2.SecurityGroup(
            "meal-planner-storage-security-group",
            name=f"{config.app_name}-storage",
            description="Controls access to persistent storage (EFS); only allows NFS from the web server",
            vpc_id=self.vpc.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Allow Lambda to reach EFS over NFS.
        # Note: source_security_group_id means *destination* for egress rules —
        # this restricts outbound NFS to only resources in the storage security group.
        aws.ec2.SecurityGroupRule(
            "meal-planner-web-server-to-storage-nfs-egress",
            type="egress",
            from_port=2049,
            to_port=2049,
            protocol="tcp",
            source_security_group_id=self.storage_security_group.id,
            security_group_id=self.web_server_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Allow outbound HTTPS so Lambda can reach AWS service endpoints (e.g. CloudWatch Logs).
        # When Lambda runs inside a VPC, all traffic — including calls to AWS services — goes
        # through the VPC network. The alternative is VPC Endpoints, but each costs ~$7-8/month
        # which exceeds the rest of the infrastructure cost at this scale.
        aws.ec2.SecurityGroupRule(
            "meal-planner-web-server-https-egress",
            type="egress",
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=self.web_server_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Allow NFS inbound to EFS only from the web server security group
        aws.ec2.SecurityGroupRule(
            "meal-planner-storage-nfs-ingress-from-web-server",
            type="ingress",
            from_port=2049,
            to_port=2049,
            protocol="tcp",
            source_security_group_id=self.web_server_security_group.id,
            security_group_id=self.storage_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "web_server_security_group_id": self.web_server_security_group.id,
            "storage_security_group_id": self.storage_security_group.id,
        })
