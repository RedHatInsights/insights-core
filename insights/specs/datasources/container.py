"""
Custom datasources for information from containers
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import foreach_execute
from insights.parsers import SkipException, parse_fixed_table
from insights.specs import Specs


@datasource(Specs.docker_list_containers, HostContext)
def docker_running_container_ids(broker):
    print ("20202002")
    containers = broker[Specs.docker_list_containers].content

    if any(l for l in containers if l.startswith("Usage: ")):
        raise SkipException('No data only help output.')

    rows = parse_fixed_table(containers, heading_ignore=['CONTAINER'], header_substitute=[("CONTAINER ID", "CONTAINER_ID")])

    if not rows:
        raise SkipException('No data.')

    container_ids = []
    for container in rows:
        if container["STATUS"].startswith("Up"):
            container_ids.append(container["CONTAINER_ID"])
    if container_ids:
        return container_ids
    raise SkipComponent


class LocalSpecs(Specs):
    docker_find_etc = foreach_execute(docker_running_container_ids, "/usr/local/bin/docker exec %s find /etc /opt -name '*.conf'")


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
