import pulumi
from maintenance_shell import MaintenanceShell

maintenance_shell = MaintenanceShell()

pulumi.export("instance_id", maintenance_shell.instance.id)
