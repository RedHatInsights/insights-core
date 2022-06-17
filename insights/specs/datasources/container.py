"""
Custom datasources for information from containers
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.parsers.docker_list import DockerListContainers
from insights.core.spec_factory import foreach_execute
from insights.specs import Specs


@datasource(DockerListContainers, HostContext)
def docker_running_container_ids(broker):
    containers = broker[DockerListContainers]
    container_ids = []
    for container in containers.rows:
        if container["STATUS"].startswith("Up"):
            container_ids.append(container["CONTAINER ID"])
    if container_ids:
        return container_ids
    raise SkipComponent


class LocalSpecs(Specs):
    docker_find_etc = foreach_execute(docker_running_container_ids, "/usr/bin/docker exec %s find /etc /opt -name '*.conf'")


@datasource(LocalSpecs.docker_find_etc, HostContext)
def docker_running_container_nginx_conf(broker):
    result_pairs = []
    for item in broker[LocalSpecs.docker_find_etc]:
        content = item.content
        container_id = item.cmd.split(" ")[2].strip()
        for line in content:
            if line.startswith("/etc/nginx"):
                result_pairs.append((container_id, line.strip()))
    if result_pairs:
        return result_pairs
    raise SkipComponent
