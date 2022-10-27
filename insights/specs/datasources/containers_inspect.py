"""
Custom datasources for containers inspect information
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, foreach_execute
from insights.core.filters import get_filters
from insights.specs import Specs
import json
from insights.specs.datasources.container import running_rhel_containers


@datasource(running_rhel_containers, HostContext)
def running_rhel_containers_id(broker):
    """
    Returns a list of container_id of the running containers.
    """
    containers_info = []
    for container in broker[running_rhel_containers]:
        containers_info.append((container[1], container[2]))
    if containers_info:
        return containers_info
    raise SkipComponent


class LocalSpecs(Specs):
    """ Local specs used only by docker|podman_inspect datasources """

    containers_inspect_data_raw = foreach_execute(running_rhel_containers_id, "/usr/bin/%s inspect %s")
    """ Returns the output of command ``/usr/bin/docker|podman inspect <container ID>`` """


@datasource(LocalSpecs.containers_inspect_data_raw, HostContext)
def containers_inspect_data_datasource(broker):
    """
    This datasource provides the filtered information collected
    from ``/usr/bin/docker|podman inspect <container ID>``.

    Typical content of ``/usr/bin/docker|podman inspect <container ID>`` file is::

        [
            {
                "Id": "aeaea3ead52724bb525bb2b5c619d67836250756920f0cb9884431ba53b476d8",
                "Created": "2022-10-21T23:47:24.506159696-04:00",
                "Path": "sleep"
                ...
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
        filters = get_filters(Specs.containers_inspect_vars)
        contents = []
        for item in broker[LocalSpecs.containers_inspect_data_raw]:
            engine = item.cmd.split()[0].split("bin/")[-1]
            contents.append((item.content, engine))
        if contents and filters:
            total_results = []
            for content in contents:
                content_raw = "".join(content[0])
                raw_data = json.loads(content_raw)[0]
                filter_result = {}
                filter_result['Id'] = raw_data['Id']
                filter_result['Image'] = raw_data['Image'].split("sha256:")[-1]
                filter_result['engine'] = content[1]
                for item in filters:
                    path = []
                    for val in _find(raw_data, item, path):
                        mid_data = {item: val}
                        for path_item in path:
                            mid_data = {path_item: mid_data}
                        filter_result.update(mid_data)
                total_results.append(filter_result)
            if total_results:
                return DatasourceProvider(content=json.dumps(total_results), relative_path='insights_commands/containers_inspect')
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent
