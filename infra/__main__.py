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
