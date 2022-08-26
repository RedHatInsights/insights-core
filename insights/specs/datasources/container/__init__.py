"""
Basic datasources for container specs
"""
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.context import HostContext
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT
from insights.parsers.podman_list import PodmanListContainers
from insights.parsers.docker_list import DockerListContainers


@datasource([PodmanListContainers, DockerListContainers], HostContext)
def running_rhel_containers(broker):
    """
    Returns a list of tuple of (image, <podman|docker>, container_id) of the running
    containers.
    """
    def _is_rhel_image(ctx, c_info):
        """Only collect the containers based from RHEL images"""
        try:
            ret = ctx.shell_out("/usr/bin/%s exec %s cat /etc/redhat-release" % c_info, timeout=DEFAULT_SHELL_TIMEOUT)
            if ret and "red hat enterprise linux" in ret[0].lower():
                return True
        except Exception:
            # return False when there is no such file "/etc/redhat-releas"
            pass
        return False

    cs = []
    if (PodmanListContainers in broker):
        podman_c = broker[PodmanListContainers]
        for name in podman_c.running_containers:
            c_info = ('podman', podman_c.containers[name]['CONTAINER ID'][:12])
            cs.append((podman_c.containers[name]['IMAGE'],) + c_info) if _is_rhel_image(broker[HostContext], c_info) else None
    if (DockerListContainers in broker):
        docker_c = broker[DockerListContainers]
        for name in docker_c.running_containers:
            c_info = ('docker', docker_c.containers[name]['CONTAINER ID'][:12])
            cs.append((docker_c.containers[name]['IMAGE'],) + c_info) if _is_rhel_image(broker[HostContext], c_info) else None
    if cs:
        # Return list of tuple:
        # - (image, <podman|docker>, container_id)
        return cs

    raise SkipComponent
