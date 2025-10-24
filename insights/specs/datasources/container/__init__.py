"""
Basic datasources for container specs
"""

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import PATH_ENV_OVERRIDER
from insights.parsers.docker_list import DockerListContainers
from insights.parsers.podman_list import PodmanListContainers
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT


@datasource([PodmanListContainers, DockerListContainers], HostContext, timeout=240)
def containers_with_shell(broker):
    """
    Returns a list of tuple of (image, <podman|docker>, container_id) of the
    running containers with /bin/sh shell available.

    From RHEL 8, the "docker" command is from the package "podman-docker". In
    general when using command "docker" to access a container, the following
    message will be reported on the top::

        Emulate Docker CLI using podman. Create /etc/containers/nodocker to quiet msg.

    But sometimes, this line won't be outputted as expected, in this case, it's
    necessary to remove the duplicated containers from the output of "docker".
    """

    def _is_shell_available_image(ctx, c_info):
        """Only collect the containers with shell"""
        try:
            engine, cid = c_info
            shell_exec_path = "/bin/sh"
            # the_cmd = <podman|docker> cp container_id:/bin/sh -
            the_cmd = '/usr/bin/%s cp %s:%s -' % (engine, cid, shell_exec_path)
            rc, _ = ctx.shell_out(the_cmd, split=False, keep_rc=True, timeout=DEFAULT_SHELL_TIMEOUT)
            if rc == 0:
                return True
        except Exception:
            pass
        return False

    cs = []
    podman_container = set()
    if PodmanListContainers in broker:
        podman_c = broker[PodmanListContainers]
        for name in podman_c.running_containers:
            container_id = podman_c.containers[name]['CONTAINER ID']
            podman_container.add(container_id)
            c_info = ('podman', container_id[:12])
            if not _is_shell_available_image(broker[HostContext], c_info):
                # skip containers from non-shell-available image
                continue
            cs.append((podman_c.containers[name]['IMAGE'],) + c_info)
    if DockerListContainers in broker:
        docker_c = broker[DockerListContainers]
        for name in docker_c.running_containers:
            container_id = docker_c.containers[name]['CONTAINER ID']
            c_info = ('docker', container_id[:12])
            if container_id in podman_container or not _is_shell_available_image(
                broker[HostContext], c_info
            ):
                # skip containers from non-shell-available image and
                # skip duplicated containers managed by "podman"
                continue
            cs.append((docker_c.containers[name]['IMAGE'],) + c_info)
    if cs:
        # Return list of tuple:
        # - (image, <podman|docker>, container_id)
        return cs

    raise SkipComponent


@datasource(containers_with_shell, HostContext, timeout=240)
def running_rhel_containers(broker):
    """
    Returns a list of tuple of (image, <podman|docker>, container_id) of the
    running rhel containers.
    """

    def _is_rhel_image(ctx, c_info):
        """Only collect the containers based from RHEL images"""
        try:
            _, engine, cid = c_info
            # cmd with existence pre_check of `cat`
            cmd = 'sh -c "command -v cat > /dev/null && cat /etc/redhat-release"'
            # the_cmd = <podman|docker> exec -e <env> container_id cmd
            the_cmd = '/usr/bin/%s exec -e "%s" %s %s' % (engine, PATH_ENV_OVERRIDER, cid, cmd)
            ret = ctx.shell_out(the_cmd, timeout=DEFAULT_SHELL_TIMEOUT)
            if ret and len(ret) == 1 and "red hat enterprise linux" in ret[0].lower():
                return True
        except Exception:
            # return False when there is no such file "/etc/redhat-release"
            pass
        return False

    cs = [c for c in broker[containers_with_shell] if _is_rhel_image(broker[HostContext], c)]
    if cs:
        return cs

    raise SkipComponent
