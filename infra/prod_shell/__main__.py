import pulumi
from networking import ShellNetworking
from shell_instance import ShellInstance
from storage import ShellStorage

networking = ShellNetworking()
storage = ShellStorage(networking)
shell = ShellInstance(networking=networking, storage=storage)

pulumi.export("instance_id", shell.instance.id)
pulumi.export("public_ip", shell.instance.public_ip)
pulumi.export("file_system_id", storage.file_system.id)
