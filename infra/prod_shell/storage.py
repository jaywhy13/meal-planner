import pulumi
import pulumi_aws as aws

import config
from networking import ShellNetworking


class ShellStorage(pulumi.ComponentResource):
    # Where the file system is mounted on the shell instance
    mount_path = "/mnt/data"

    # Directory on the file system the access point is scoped to
    root_directory = "/meal-planner"

    def __init__(self, networking: ShellNetworking):
        super().__init__(
            "meal-planner:prod_shell:ShellStorage",
            f"{config.app_name}-storage",
            {},
        )

        self.file_system = aws.efs.FileSystem(
            f"{config.app_name}-file-system",
            encrypted=True,
            performance_mode="generalPurpose",
            throughput_mode="elastic",
            tags={"Name": f"{config.app_name}-storage"},
            opts=pulumi.ResourceOptions(parent=self),
        )

        aws.efs.BackupPolicy(
            f"{config.app_name}-backup-policy",
            file_system_id=self.file_system.id,
            backup_policy=aws.efs.BackupPolicyBackupPolicyArgs(status="ENABLED"),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # NFS traffic doesn't cross availability zones, so the mount target lives in the
        # same subnet as the shell instance.
        self.mount_target = aws.efs.MountTarget(
            f"{config.app_name}-mount-target",
            file_system_id=self.file_system.id,
            subnet_id=networking.subnet.id,
            security_groups=[networking.storage_security_group.id],
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.file_system]),
        )

        # Mirrors the access point the Lambda function uses: the shell's view of the file
        # system is scoped to /meal-planner rather than the root.
        self.access_point = aws.efs.AccessPoint(
            f"{config.app_name}-access-point",
            file_system_id=self.file_system.id,
            posix_user=aws.efs.AccessPointPosixUserArgs(uid=1001, gid=1001),
            root_directory=aws.efs.AccessPointRootDirectoryArgs(
                path=self.root_directory,
                creation_info=aws.efs.AccessPointRootDirectoryCreationInfoArgs(
                    owner_uid=1001,
                    owner_gid=1001,
                    permissions="755",
                ),
            ),
            tags={"Name": f"{config.app_name}-access-point"},
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "file_system_id": self.file_system.id,
            "access_point_id": self.access_point.id,
            "mount_path": self.mount_path,
        })
