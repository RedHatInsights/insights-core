"""
Custom datasources for awx_manage information
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, foreach_execute
from insights.core.filters import get_filters
from insights.specs import Specs
import json
from insights.specs.datasources import DEFAULT_SHELL_TIMEOUT
# from insights.parsers.podman_list import PodmanListContainers
from insights.parsers.docker_list import DockerListContainers


@datasource(DockerListContainers, HostContext)
def running_docker_rhel_containers(broker):
    """
    Returns a list of container_id of the running containers.
    """
    def _is_rhel_image(ctx, c_info):
        """Only collect the containers based from RHEL images"""
        try:
            ret = ctx.shell_out("/usr/bin/docker exec %s cat /etc/redhat-release" % c_info, timeout=DEFAULT_SHELL_TIMEOUT)
            if ret and "red hat enterprise linux" in ret[0].lower():
                return True
        except Exception:
            # return False when there is no such file "/etc/redhat-releas"
            pass
        return False

    cs = []
    if (DockerListContainers in broker):
        docker_c = broker[DockerListContainers]
        for name in docker_c.running_containers:
            c_info = docker_c.containers[name]['CONTAINER ID'][:12]
            cs.append(c_info) if _is_rhel_image(broker[HostContext], c_info) else None
    if cs:
        return cs
    raise SkipComponent


class LocalSpecs(Specs):
    """ Local specs used only by docker_inspect datasources """

    docker_container_inspect_data_raw = foreach_execute(running_docker_rhel_containers, "/usr/bin/docker inspect %s")
    """ Returns the output of command ``/usr/bin/docker inspect <container ID>`` """


@datasource(LocalSpecs.docker_container_inspect_data_raw, HostContext)
def docker_container_inspect_data_datasource(broker):
    """
    This datasource provides the filtered information collected
    from ``/usr/bin/docker inspect <container ID>``.

    Typical content of ``/usr/bin/docker inspect <container ID>`` file is::

        [
            {
                "Id": "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8",
                "Created": "2022-10-21T23:47:24.506159696-04:00",
                "Path": "sleep"
            }
            ...
        ]
    Returns:
        list: item is JSON string containing filtered information.

    Raises:
        SkipComponent: When the filter/path does not exist or any exception occurs.
    """
    def _find(d, tag, path):
        if tag in d:
            yield d[tag]
        for k, v in d.items():
            if isinstance(v, dict):
                for i in _find(v, tag, path):
                    path.append(k)
                    yield i

    try:
        filters = get_filters(Specs.docker_container_inspect)
        contents = []
        for item in broker[LocalSpecs.docker_container_inspect_data_raw]:
            contents.append(item.content)
        if contents and filters:
            total_results = []
            for content in contents:
                content = "".join(content)
                raw_data = json.loads(content)[0]
                filter_result = {}
                filter_result['Id'] = raw_data['Id']
                filter_result['Image'] = raw_data['Image']
                filter_result['ImageName'] = raw_data['ImageName']
                for item in filters:
                    path = []
                    for val in _find(raw_data, item, path):
                        mid_data = {item: val}
                        for path_item in path:
                            mid_data = {path_item: mid_data}
                        filter_result.update(mid_data)
                total_results.append(filter_result)
            if total_results:
                return DatasourceProvider(content=json.dumps(total_results), relative_path='insights_commands/docker_inspect')
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent
