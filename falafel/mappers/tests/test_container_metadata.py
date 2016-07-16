from falafel.core.context import Docker
from falafel.mappers.container_metadata import docker_metadata_role
from falafel.tests import context_wrap, RHEL7, RHEL6

docker_h = Docker()
docker_h.role = "host"

docker_c = Docker()
docker_c.role = "container"

docker_i = Docker()
docker_i.role = "image"


def test_container_metadata():
    context = context_wrap(RHEL6, docker=docker_c)
    assert docker_metadata_role(context)
    assert docker_metadata_role(context).is_container()

    context = context_wrap(RHEL7, docker=docker_i)
    assert docker_metadata_role(context)
    assert docker_metadata_role(context).is_image()

    context = context_wrap(RHEL7, docker=docker_h)
    assert docker_metadata_role(context)
    assert docker_metadata_role(context).is_host()

    # Test that a non-docker related system is False
    context = context_wrap(RHEL7)
    assert docker_metadata_role(context) is None

    # Test that an empty redhat-release file in a container is True
    context = context_wrap(None, docker=docker_c)
    assert docker_metadata_role(context)
    assert docker_metadata_role(context).is_container()
