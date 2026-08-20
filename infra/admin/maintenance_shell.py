import json
from pathlib import Path

import pulumi
import pulumi_aws as aws

import config

_USER_DATA_TEMPLATE = Path(__file__).parent.joinpath("user_data.sh").read_text()


class MaintenanceShell(pulumi.ComponentResource):
    def __init__(self):
        super().__init__(
            "meal-planner:maintenance_shell:MaintenanceShell", "meal-planner-maintenance-shell", {}
        )

        # Amazon Linux 2023 ships the Systems Manager agent preinstalled, which is
        # what makes shell access without a key pair or open port 22 possible.
        ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(name="name", values=["al2023-ami-*-x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )

        self.role = aws.iam.Role(
            "meal-planner-maintenance-shell-role",
            name=f"{config.app_name}-maintenance-shell-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{
                    "Effect": "Allow",
                    "Principal": {"Service": "ec2.amazonaws.com"},
                    "Action": "sts:AssumeRole",
                }],
            }),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Lets Session Manager register this instance and open a shell on it —
        # this, not a security group ingress rule, is what makes "ssh" possible.
        aws.iam.RolePolicyAttachment(
            "meal-planner-maintenance-shell-systems-manager-policy",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Allows mounting and reading/writing the app's EFS volume over IAM auth,
        # matching how web_server.py grants the same policy to the Lambda role.
        aws.iam.RolePolicyAttachment(
            "meal-planner-maintenance-shell-efs-policy",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonElasticFileSystemClientReadWriteAccess",
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.instance_profile = aws.iam.InstanceProfile(
            "meal-planner-maintenance-shell-instance-profile",
            name=f"{config.app_name}-maintenance-shell-instance-profile",
            role=self.role.name,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.security_group = aws.ec2.SecurityGroup(
            "meal-planner-maintenance-shell-security-group",
            name=f"{config.app_name}-maintenance-shell",
            description=(
                "Outbound-only for the maintenance shell: Systems Manager (443) and "
                "NFS to storage (2049). No ingress rules — access is via Session "
                "Manager, never a listening port."
            ),
            vpc_id=config.vpc_id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # The subnet is public with an internet gateway route, so Session Manager's
        # HTTPS endpoints are reachable directly — no VPC endpoint needed, matching
        # the cost trade-off networking.py already made for the web server.
        aws.ec2.SecurityGroupRule(
            "meal-planner-maintenance-shell-systems-manager-egress",
            type="egress",
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=self.security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.ec2.SecurityGroupRule(
            "meal-planner-maintenance-shell-storage-nfs-egress",
            type="egress",
            from_port=2049,
            to_port=2049,
            protocol="tcp",
            source_security_group_id=config.storage_security_group_id,
            security_group_id=self.security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Attaches an ingress rule to the app stack's storage security group from
        # this stack. Safe to do: networking.py declares NFS rules as standalone
        # SecurityGroupRule resources rather than an inline ingress=[...] block, so
        # two stacks can each attach a rule to the same group without fighting over
        # its state. Do not change networking.py to inline rules — that would break
        # this.
        aws.ec2.SecurityGroupRule(
            "meal-planner-maintenance-shell-storage-nfs-ingress",
            type="ingress",
            from_port=2049,
            to_port=2049,
            protocol="tcp",
            source_security_group_id=self.security_group.id,
            security_group_id=config.storage_security_group_id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # The access point id and file system id are only known once the app stack
        # has actually deployed (see config.py), so the template is filled in inside
        # an apply() rather than an f-string.
        #
        # Plain string.replace() rather than str.format(): the template is a shell
        # script, and both str.format() and string.Template would collide with the
        # first "${VAR}" or "{print $1}" anyone adds to it, failing pulumi up with
        # a confusing KeyError far from the actual cause.
        user_data = pulumi.Output.all(
            file_system_id=config.file_system_id,
            access_point_id=config.access_point_id,
        ).apply(
            lambda args: _USER_DATA_TEMPLATE.replace(
                "__FILE_SYSTEM_ID__", args["file_system_id"]
            ).replace("__ACCESS_POINT_ID__", args["access_point_id"])
        )

        self.instance = aws.ec2.Instance(
            "meal-planner-maintenance-shell-instance",
            ami=ami.id,
            instance_type="t3.micro",
            subnet_id=config.subnet_id,
            vpc_security_group_ids=[self.security_group.id],
            iam_instance_profile=self.instance_profile.name,
            # The subnet's own "assign public IP on launch" setting isn't something
            # this stack owns or can rely on, so it's requested explicitly — without
            # a public IP, this instance has no path to the Systems Manager
            # endpoints and Session Manager can never connect to it.
            associate_public_ip_address=True,
            user_data=user_data,
            tags={"Name": f"{config.app_name}-maintenance-shell"},
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "instance_id": self.instance.id,
        })
