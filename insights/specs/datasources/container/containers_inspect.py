"""
Custom datasources for containers inspect information
"""
import json
import os

from insights.core.context import HostContext
from insights.core.exceptions import ContentException, SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, foreach_execute
from insights.specs import Specs
from insights.specs.datasources.container import running_rhel_containers


@datasource(running_rhel_containers, HostContext)
def running_rhel_containers_id(broker):
    """
    Returns a list of container_id of the running containers.
    """
    containers_info = []
    for container in broker[running_rhel_containers]:
        containers_info.append((container[1], container[2]))
    return containers_info


class LocalSpecs(Specs):
    """ Local specs used only by docker|podman inspect datasources """

    containers_inspect_data_raw = foreach_execute(running_rhel_containers_id, "/usr/bin/%s inspect %s")
    """ Returns the output of command ``/usr/bin/docker|podman inspect <container ID>`` """


@datasource(LocalSpecs.containers_inspect_data_raw, HostContext)
def containers_inspect_data_datasource(broker):
    """
    This datasource provides the filtered information collected
    from ``/usr/bin/docker|podman inspect <container ID>``.

    .. note::
        The path of the target key is like raw_data[key1][key2][target_key],
        then the filter pattern is like "key1|key2|target_key".
        If the value type of raw_data[key1][key2] is list, although the target_key is in the list,
        the filter pattern must be "key1|key2", this datasource returns the whole value of the list.
        The value of "Id" and "Image" are checked from raw data directly, no need filter these items.

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
    try:
        no_filters = ['Id', 'Image']
        filters = sorted(set(get_filters(Specs.container_inspect_keys)) - set(no_filters))
        if filters:
            total_results = []
            for item in broker[LocalSpecs.containers_inspect_data_raw]:
                raw_data = json.loads(''.join(item.content))[0]
                engine, _, container_id = item.cmd.split(None)
                filter_result = dict(Id=container_id, engine=os.path.basename(engine))
                if 'Image' in raw_data:
                    filter_result['Image'] = raw_data['Image'].split("sha256:")[-1]
                for item in filters:
                    val = raw_data
                    for key in item.split("|"):
                        if key in val:
                            val = val[key]
                        else:
                            break
                    # If the filtered key does not exist, skip it
                    if val == raw_data:
                        continue
                    filter_result[item] = val
                total_results.append(filter_result)
            # Generally the False branch of this condition will never reach, since the required component
            # LocalSpecs.containers_inspect_data_raw can guarantee total_results is not null. However, it's worth
            # leaving this condition as an explicit assertion to avoid unexpected situation.
            if total_results:
                return DatasourceProvider(content=json.dumps(total_results), relative_path='insights_containers/containers_inspect')
    except Exception as e:
        raise ContentException("Unexpected content exception:{e}".format(e=str(e)))
    raise SkipComponent
