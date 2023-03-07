"""
Custom datasource to get the duplicate machine id.
"""
import json
import logging
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.specs import Specs
from insights.client.config import InsightsConfig
from insights.client.connection import InsightsConnection
from insights.client.auto_config import try_auto_configuration
from insights.core.spec_factory import DatasourceProvider

logger = logging.getLogger(__name__)


@datasource(HostContext)
def dup_machine_id(broker):
    """
    This datasource provides the duplicate machine id.

    Returns:
        str: a string containing the machine id.

    Raises:
        SkipComponent: When the filters does not exist or the machine id is not
           in the filters or the machine id is not duplicate or any exception
           occurs.
    """
    filters = sorted((get_filters(Specs.duplicate_machine_id)))
    if not filters or Specs.machine_id not in broker:
        raise SkipComponent
    machine_id_obj = broker[Specs.machine_id]
    if machine_id_obj and machine_id_obj.content and len(machine_id_obj.content) == 1:
        machine_id = str(machine_id_obj.content[0].strip())
        if machine_id in filters:
            config = InsightsConfig()
            config._load_config_file()
            config._load_env()
            try_auto_configuration(config)
            conn = InsightsConnection(config)
            try:
                if config.legacy_upload:
                    url = conn.base_url + '/platform/inventory/v1/hosts?insights_id=' + machine_id
                else:
                    url = conn.inventory_url + '/hosts?insights_id=' + machine_id
                res = conn.get(url)
            except Exception:
                raise SkipComponent
            try:
                res_json = json.loads(res.content)
            except ValueError:
                raise SkipComponent
            if res_json['total'] > 1:
                return DatasourceProvider(content=[machine_id], relative_path='insights_commands/duplicate_machine_id')
    raise SkipComponent
