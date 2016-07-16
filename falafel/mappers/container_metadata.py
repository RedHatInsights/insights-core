from falafel.core.plugins import mapper
from falafel.core import MapperOutput


class DockerRole(MapperOutput):

    def is_host(self):
        return self["role"].lower() == "host"

    def is_container(self):
        return self["role"].lower() == "container"

    def is_image(self):
        return self["role"].lower() == "image"


@mapper("redhat-release")
def docker_metadata_role(context):
    """
    Return true if we are processing a docker container or image

    The use of /etc/redhat-release is simply to get access to the context
    metadata to work out if we are processing a container/image or not.
    It's assumed that /etc/redhat-release will be available regardless whether
    the 'system' is a RHEL host, container or image
    """
    if context.docker and context.docker.role:
        return DockerRole({"role": context.docker.role})
