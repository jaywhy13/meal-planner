import json
from typing import Optional

import pulumi
import pulumi_aws as aws

import config
from networking import ShellNetworking
from storage import ShellStorage

USER_DATA_TEMPLATE = """#!/bin/bash
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y python3.10 python3.10-venv python3-pip sqlite3 nfs-common git awscli

# Ubuntu images ship the SSM agent as a snap; it is what Session Manager connects to.
snap start amazon-ssm-agent || systemctl enable --now snap.amazon-ssm-agent.amazon-ssm-agent.service

mount_options="nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport"
file_system_host="{file_system_id}.efs.{aws_region}.amazonaws.com"

# The access point directory has to exist on the file system before it can be mounted
# on its own, so the root of the file system is mounted once to create it.
mkdir -p /mnt/efs-root {mount_path}
until mount -t nfs4 -o "$mount_options" "$file_system_host":/ /mnt/efs-root; do sleep 10; done
mkdir -p "/mnt/efs-root{root_directory}"
chown 1001:1001 "/mnt/efs-root{root_directory}"
chmod 755 "/mnt/efs-root{root_directory}"
umount /mnt/efs-root
rmdir /mnt/efs-root

echo "$file_system_host:{root_directory} {mount_path} nfs4 $mount_options,_netdev 0 0" >> /etc/fstab
mount {mount_path}

mkdir -p /root/.ssh
chmod 700 /root/.ssh
aws ssm get-parameter --name "{deploy_key_parameter_name}" --with-decryption --region "{aws_region}" \
    --query Parameter.Value --output text > /root/.ssh/id_ed25519
chmod 600 /root/.ssh/id_ed25519

# The parameter holds "{deploy_key_placeholder}" until an operator sets the deploy key,
# in which case the repository is cloned by hand instead.
if [ "$(cat /root/.ssh/id_ed25519)" = "{deploy_key_placeholder}" ]; then
    rm -f /root/.ssh/id_ed25519
else
    ssh-keyscan github.com >> /root/.ssh/known_hosts
    git clone "{repository_url}" /app
fi

python3.10 -m venv /opt/django-env
/opt/django-env/bin/pip install --upgrade pip uv

cat > /usr/local/bin/manage <<'MANAGE'
#!/bin/bash
set -euo pipefail
export DATABASE_URL="{database_url}"
cd /app/backend
exec /opt/django-env/bin/python manage.py "$@"
MANAGE
chmod +x /usr/local/bin/manage

if [ -d /app/backend ]; then
    cd /app/backend
    /opt/django-env/bin/uv export --no-dev --no-hashes --format requirements-txt -o /tmp/requirements.txt
    /opt/django-env/bin/pip install -r /tmp/requirements.txt
    manage migrate --noinput
fi

cat > /etc/profile.d/meal-planner.sh <<'PROFILE'
export DATABASE_URL="{database_url}"
export PATH="/opt/django-env/bin:$PATH"
PROFILE
"""


DEPLOY_KEY_PLACEHOLDER = "unset"


class ShellInstance(pulumi.ComponentResource):
    def __init__(self, networking: ShellNetworking, storage: ShellStorage):
        super().__init__(
            "meal-planner:prod_shell:ShellInstance",
            f"{config.app_name}-instance",
            {},
        )

        self.deploy_key_parameter = self._create_deploy_key_parameter()
        self.role = self._create_role()
        self._attach_role_policies(storage)
        instance_profile = aws.iam.InstanceProfile(
            f"{config.app_name}-instance-profile",
            name=f"{config.app_name}-instance-profile",
            role=self.role.name,
            opts=pulumi.ResourceOptions(parent=self),
        )

        ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["099720109477"],
            filters=[
                aws.ec2.GetAmiFilterArgs(
                    name="name",
                    values=["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"],
                ),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
            ],
        )

        self.instance = aws.ec2.Instance(
            f"{config.app_name}-instance",
            ami=ami.id,
            instance_type=config.instance_type,
            subnet_id=networking.subnet.id,
            vpc_security_group_ids=[networking.shell_security_group.id],
            iam_instance_profile=instance_profile.name,
            # Session Manager reaches the instance through an outbound connection the SSM
            # agent opens, which needs a route to the internet.
            associate_public_ip_address=True,
            user_data=self._render_user_data(storage),
            user_data_replace_on_change=True,
            tags={"Name": config.app_name},
            opts=pulumi.ResourceOptions(parent=self, depends_on=[storage.mount_target]),
        )

        self.register_outputs({
            "instance_id": self.instance.id,
            "public_ip": self.instance.public_ip,
        })

    def _create_deploy_key_parameter(self) -> aws.ssm.Parameter:
        return aws.ssm.Parameter(
            f"{config.app_name}-deploy-key",
            name=f"/{config.app_name}/github-deploy-key",
            type="SecureString",
            value=config.github_deploy_key or DEPLOY_KEY_PLACEHOLDER,
            opts=pulumi.ResourceOptions(parent=self),
        )

    def _create_role(self) -> aws.iam.Role:
        return aws.iam.Role(
            f"{config.app_name}-role",
            name=f"{config.app_name}-role",
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

    def _attach_role_policies(self, storage: ShellStorage) -> None:
        # Everything the SSM agent needs to register the instance and serve Session
        # Manager sessions. Session Manager permissions for operators are granted to the
        # human's own credentials, not to this role.
        aws.iam.RolePolicyAttachment(
            f"{config.app_name}-ssm-managed-instance-policy",
            role=self.role.name,
            policy_arn="arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.iam.RolePolicy(
            f"{config.app_name}-deploy-key-policy",
            role=self.role.name,
            policy=self.deploy_key_parameter.arn.apply(
                lambda arn: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": ["ssm:GetParameter"],
                        "Resource": arn,
                    }],
                })
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.iam.RolePolicy(
            f"{config.app_name}-storage-policy",
            role=self.role.name,
            policy=storage.file_system.arn.apply(
                lambda arn: json.dumps({
                    "Version": "2012-10-17",
                    "Statement": [{
                        "Effect": "Allow",
                        "Action": [
                            "elasticfilesystem:ClientMount",
                            "elasticfilesystem:ClientWrite",
                            "elasticfilesystem:ClientRootAccess",
                        ],
                        "Resource": arn,
                    }],
                })
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

    def _render_user_data(self, storage: ShellStorage) -> pulumi.Output[str]:
        return pulumi.Output.all(
            file_system_id=storage.file_system.id,
            deploy_key_parameter_name=self.deploy_key_parameter.name,
        ).apply(
            lambda values: USER_DATA_TEMPLATE.format(
                file_system_id=values["file_system_id"],
                deploy_key_parameter_name=values["deploy_key_parameter_name"],
                aws_region=config.aws_region,
                mount_path=storage.mount_path,
                root_directory=storage.root_directory,
                repository_url=config.repository_url,
                deploy_key_placeholder=DEPLOY_KEY_PLACEHOLDER,
                # Four slashes: sqlite:// (scheme) + // (empty host) + absolute path
                database_url=f"sqlite:///{storage.mount_path}/db.sqlite3",
            )
        )

    @property
    def public_ip(self) -> pulumi.Output[Optional[str]]:
        return self.instance.public_ip
