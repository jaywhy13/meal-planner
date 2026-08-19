import pulumi
from networking import AppNetworking
from storage import AppStorage
from container_image import ContainerImage
from monitoring import AppMonitoring
from web_server import WebServer

networking = AppNetworking()
storage = AppStorage(networking)
image = ContainerImage()
monitoring = AppMonitoring()
web_server = WebServer(
    image=image,
    storage=storage,
    networking=networking,
    monitoring=monitoring,
)

pulumi.export("url", web_server.url)

# Read by infra/admin/'s StackReference so the on-demand maintenance instance
# can mount the same EFS file system and open a locked-down NFS path into the
# same storage security group, without this stack's state file ever changing.
pulumi.export("vpc_id", networking.vpc.id)
pulumi.export("subnet_id", networking.subnet.id)
pulumi.export("storage_security_group_id", networking.storage_security_group.id)
pulumi.export("file_system_id", storage.file_system.id)
pulumi.export("access_point_id", storage.access_point.id)
