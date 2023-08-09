"""
Basic datasources for container specs
"""
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.docker_list import DockerListContainers
from insights.parsers.podman_list import PodmanListContainers
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT


@datasource([PodmanListContainers, DockerListContainers], HostContext, timeout=240)
def running_rhel_containers(broker):
    """
    Returns a list of tuple of (image, <podman|docker>, container_id) of the running
    containers.

    From RHEL 8, the "docker" command is from the package "podman-docker". In
    general when using command "docker" to access a container, the following
    message will be reported on the top::

        Emulate Docker CLI using podman. Create /etc/containers/nodocker to quiet msg.

    But sometimes, this line won't be outputted as expected, in this case, it's
    necessary to remove the duplicated containers from the output of "docker".
    """
    def _is_rhel_image(ctx, c_info):
        """Only collect the containers based from RHEL images"""
        try:
            ret = ctx.shell_out("/usr/bin/%s exec %s cat /etc/redhat-release" % c_info, timeout=DEFAULT_SHELL_TIMEOUT)
            if ret and len(ret) == 1 and "red hat enterprise linux" in ret[0].lower():
                return True
        except Exception:
            # return False when there is no such file "/etc/redhat-releas"
            pass
        return False

    cs = []
    podman_container = set()
    if (PodmanListContainers in broker):
        podman_c = broker[PodmanListContainers]
        for name in podman_c.running_containers:
            container_id = podman_c.containers[name]['CONTAINER ID']
            podman_container.add(container_id)
            c_info = ('podman', container_id[:12])
            if not _is_rhel_image(broker[HostContext], c_info):
                # skip containers from non-rhel image
                continue
            cs.append((podman_c.containers[name]['IMAGE'],) + c_info)
    if (DockerListContainers in broker):
        docker_c = broker[DockerListContainers]
        for name in docker_c.running_containers:
            container_id = docker_c.containers[name]['CONTAINER ID']
            c_info = ('docker', container_id[:12])
            if (container_id in podman_container or
                    not _is_rhel_image(broker[HostContext], c_info)):
                # skip containers from non-rhel image and
                # skip duplicated containers managed by "podman"
                continue
            cs.append((docker_c.containers[name]['IMAGE'],) + c_info)
    if cs:
        # Return list of tuple:
        # - (image, <podman|docker>, container_id)
        return cs

    raise SkipComponent
