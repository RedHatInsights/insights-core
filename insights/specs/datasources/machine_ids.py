"""
Custom datasource to get the duplicate machine info.
"""
import json

from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.core.filters import get_filters
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.client.client import get_connection
from insights.specs import Specs


@datasource(HostContext, Specs.machine_id)
def dup_machine_id_info(broker):
    """
    This datasource provides the duplicate machine info.

    Sample Output::

        dc194312-8cdd-4e75-8cf1-2094bf666f45 hostname1,hostname2

    Returns:
        str: a string containing the machine id and the hostnames with the same machine id

    Raises:
        SkipComponent: When the filters does not exist or the machine id is not
           in the filters or the machine id is not duplicate or any exception
           occurs.
    """
    filters = sorted((get_filters(Specs.duplicate_machine_id)))
    if not filters:
        raise SkipComponent
    machine_id_obj = broker[Specs.machine_id]
    if len(machine_id_obj.content) == 1:
        machine_id = str(machine_id_obj.content[0].strip())
        if machine_id in filters:
            config = broker.get('client_config')
            try:
                conn = get_connection(config)
                if config.legacy_upload:
                    url = conn.base_url + '/platform/inventory/v1/hosts?insights_id=' + machine_id
                else:
                    url = conn.inventory_url + '/hosts?insights_id=' + machine_id
                res = conn.get(url)
                res_json = json.loads(res.content)
            except Exception:
                raise SkipComponent
            if res_json['total'] > 1:
                duplicate_hostnames = [item.get('fqdn') for item in res_json['results'] if item.get('fqdn')]
                content = '%s %s' % (machine_id, ','.join(duplicate_hostnames))
                return DatasourceProvider(content=[content], relative_path='insights_commands/duplicate_machine_id_info')
    raise SkipComponent
