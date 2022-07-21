"""
Custom datasource for ..
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.podman_list import PodmanListContainers
from insights.parsers.docker_list import DockerListContainers


@datasource([PodmanListContainers, DockerListContainers], HostContext)
def running_containers(broker):
    """
    """
    cs = []
    if (PodmanListContainers in broker):
        podman_c = broker[PodmanListContainers]
        for name in podman_c.running_containers:
            c_info = podman_c.containers[name]
            cs.append(('podman', c_info['CONTAINER ID']))
    if (DockerListContainers in broker):
        docker_c = broker[DockerListContainers]
        for name in docker_c.running_containers:
            c_info = docker_c.containers[name]
            cs.append(('docker', c_info['CONTAINER ID']))
    if cs:
        return cs

    raise SkipComponent


# @datasource(running_containers, HostContext)
# def ls_containers(broker):
#     """
#     """
#     podman_c = broker[running_containers]
#     ret = []
#     for p in podman_c:
#         _p = list(p)
#         _p.append('/etc')
#         ret.append(tuple(_p))
#     return ret

#     raise SkipComponent
