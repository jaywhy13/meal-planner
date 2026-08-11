import pulumi
import pulumi_aws as aws

import config


class ShellNetworking(pulumi.ComponentResource):
    def __init__(self):
        super().__init__(
            "meal-planner:prod_shell:ShellNetworking",
            f"{config.app_name}-networking",
            {},
        )

        self.vpc = aws.ec2.get_vpc(id=config.vpc_id)
        self.subnet = aws.ec2.get_subnet(id=config.subnet_id)

        # Security group attached to the shell instance. Session Manager works over an
        # outbound connection the SSM agent opens, so no inbound rules are needed.
        self.shell_security_group = aws.ec2.SecurityGroup(
            f"{config.app_name}-shell-security-group",
            name=f"{config.app_name}-shell",
            description="Controls outbound access from the prod shell instance",
            vpc_id=self.vpc.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Security group attached to the EFS mount target. Only accepts NFS from the shell.
        self.storage_security_group = aws.ec2.SecurityGroup(
            f"{config.app_name}-storage-security-group",
            name=f"{config.app_name}-storage",
            description="Controls access to the prod shell EFS file system",
            vpc_id=self.vpc.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # source_security_group_id on an egress rule means *destination* — outbound NFS
        # is restricted to the storage security group.
        aws.ec2.SecurityGroupRule(
            f"{config.app_name}-shell-to-storage-nfs-egress",
            type="egress",
            from_port=2049,
            to_port=2049,
            protocol="tcp",
            source_security_group_id=self.storage_security_group.id,
            security_group_id=self.shell_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Outbound HTTPS reaches the Session Manager, EFS and Parameter Store endpoints,
        # the Ubuntu package mirrors and GitHub over HTTPS.
        aws.ec2.SecurityGroupRule(
            f"{config.app_name}-shell-https-egress",
            type="egress",
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=self.shell_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Outbound HTTP for the Ubuntu package mirrors, which are not HTTPS by default.
        aws.ec2.SecurityGroupRule(
            f"{config.app_name}-shell-http-egress",
            type="egress",
            from_port=80,
            to_port=80,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=self.shell_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Outbound SSH so the instance can clone the repository from GitHub.
        aws.ec2.SecurityGroupRule(
            f"{config.app_name}-shell-ssh-egress",
            type="egress",
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=["0.0.0.0/0"],
            security_group_id=self.shell_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.ec2.SecurityGroupRule(
            f"{config.app_name}-storage-nfs-ingress-from-shell",
            type="ingress",
            from_port=2049,
            to_port=2049,
            protocol="tcp",
            source_security_group_id=self.shell_security_group.id,
            security_group_id=self.storage_security_group.id,
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "shell_security_group_id": self.shell_security_group.id,
            "storage_security_group_id": self.storage_security_group.id,
        })
