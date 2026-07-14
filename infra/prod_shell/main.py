import json
import pulumi
import pulumi_aws as aws

from config import app_name, vpc_id, subnet_id


# ── Security group (module-level — referenced by instance) ──────────────────
security_group = aws.ec2.SecurityGroup(
    f"{app_name}-sg",
    name=f"{app_name}",
    description="Security group for the prod shell EC2 instance — SSH, NFS to EFS access point, HTTPS outbound",
    vpc_id=vpc_id,
    ingress=[
        {
            "description": "Allow SSH from anywhere (for debugging)",
            "from_port": 22,
            "to_port": 22,
            "protocol": "tcp",
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "description": f"Allow NFS to EFS access point (port 2049) — fs ID: $FILE_SYSTEM_ID",
            "from_port": 2049,
            "to_port": 2049,
            "protocol": "tcp",
            "cidr_blocks": ["0.0.0.0/0"],  # EFS access point handles actual scoping; this is just NFS traffic allowance
        },
    ],
    egress=[
        {
            "description": "Allow outbound HTTPS for AWS service calls (CloudWatch, SSM)",
            "from_port": 443,
            "to_port": 443,
            "protocol": "tcp",
            "cidr_blocks": ["0.0.0.0/0"],
        },
        {
            "description": "Allow outbound SSH for git clone over SSH to github.com",
            "from_port": 22,
            "to_port": 22,
            "protocol": "tcp",
            "cidr_blocks": ["0.0.0.0/0"],
        },
    ],
)


class ProdShell(pulumi.Resource):
    def __init__(self):
        super().__init__("meal-planner:prod_shell:ProdShell", "meal-planner-shell", {})

        # ── IAM role with Session Manager permissions (scoped) ────────────────
        self.role = aws.iam.Role(
            f"{app_name}-role",
            name=f"{app_name}-role",
            assume_role_policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]
            }),
        )

        aws.iam.RolePolicy(
            f"{app_name}-ssm-policy",
            role=self.role.name,
            policy=json.dumps({
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ec2:DescribeInstances",
                            "iam:GetRole",
                            "iam:GetInstanceProfile",
                        ],
                        "Resource": "*",
                    },
                    # Session Manager needs these to create/manage sessions
                    {
                        "Effect": "Allow",
                        "Action": ["ssm:GetSessionName", "ssm:StartSession"],
                        "Resource": "*",
                    },
                ]
            }),
        )

        # ── Instance profile ──────────────────────────────────────────────────
        instance_profile = aws.iam.InstanceProfile(
            f"{app_name}-profile",
            name=f"{app_name}-instance-profile",
            role=self.role.name,
        )



