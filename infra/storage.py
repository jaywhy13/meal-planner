import pulumi
import pulumi_aws as aws

import config
from networking import AppNetworking


class AppStorage(pulumi.ComponentResource):
    # The path where EFS is mounted inside the Lambda execution environment
    mount_path = "/mnt/data"

    def __init__(self, networking: AppNetworking):
        super().__init__("meal-planner:storage:AppStorage", "meal-planner-storage", {})

        self.file_system = aws.efs.FileSystem(
            "meal-planner-storage-file-system",
            encrypted=True,
            performance_mode="generalPurpose",
            # Elastic throughput automatically scales with usage rather than requiring
            # a provisioned throughput value. Right-sized for a low-traffic app.
            throughput_mode="elastic",
            tags={"Name": f"{config.app_name}-storage"},
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Explicit backup policy — keeps a daily backup without needing to rely on
        # the auto-backup tag that AWS sets by default.
        aws.efs.BackupPolicy(
            "meal-planner-storage-backup-policy",
            file_system_id=self.file_system.id,
            backup_policy=aws.efs.BackupPolicyBackupPolicyArgs(status="ENABLED"),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # The mount target is the network entry point for EFS within the VPC.
        # It must live in the same subnet (and therefore the same AZ) as the Lambda
        # function — NFS traffic doesn't cross availability zones.
        self.mount_target = aws.efs.MountTarget(
            "meal-planner-storage-mount-target",
            file_system_id=self.file_system.id,
            subnet_id=networking.subnet.id,
            security_groups=[networking.storage_security_group.id],
            opts=pulumi.ResourceOptions(parent=self, depends_on=[self.file_system]),
        )

        # The access point scopes Lambda's view of EFS to a specific directory
        # (/meal-planner) rather than the root of the file system. This means
        # Lambda can only read/write within that directory, even though the
        # underlying EFS volume could hold other directories.
        #
        # posix_user sets the uid/gid that Lambda uses when accessing files through
        # this access point, controlling file ownership on the EFS side.
        #
        # root_directory.creation_info tells EFS to create the directory with these
        # ownership/permission settings if it doesn't already exist.
        self.access_point = aws.efs.AccessPoint(
            "meal-planner-storage-access-point",
            file_system_id=self.file_system.id,
            posix_user=aws.efs.AccessPointPosixUserArgs(uid=1001, gid=1001),
            root_directory=aws.efs.AccessPointRootDirectoryArgs(
                path="/meal-planner",
                creation_info=aws.efs.AccessPointRootDirectoryCreationInfoArgs(
                    owner_uid=1001,
                    owner_gid=1001,
                    permissions="755",
                ),
            ),
            tags={"Name": f"{config.app_name}-storage-access-point"},
            opts=pulumi.ResourceOptions(parent=self),
        )

        self.register_outputs({
            "file_system_id": self.file_system.id,
            "access_point_arn": self.access_point.arn,
            "mount_path": self.mount_path,
        })
