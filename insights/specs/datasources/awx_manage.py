"""
Custom datasources for awx_manage information
"""
import collections
import json

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by awx_manage datasources """

    awx_manage_check_license_data_raw = simple_command("/usr/bin/awx-manage check_license --data")
    """ Returns the output of command ``/usr/bin/awx-manage check_license --data`` """


@datasource(LocalSpecs.awx_manage_check_license_data_raw, HostContext)
def awx_manage_check_license_data_datasource(broker):
    """
    This datasource provides the not-sensitive information collected
    from ``/usr/bin/awx-manage check_license --data``.

    Typical content of ``/usr/bin/awx-manage check_license --data`` file is::

        {"contact_email": "test@redhat.com", "company_name": "test Inc", "instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "sku": "MCT3691", "support_level": "Standard", "product_name": "Red Hat Ansible Automation Platform", "valid_key": true, "satellite": null, "pool_id": "2c92808179803e530179ea5989a157a4", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}

    Returns:
        str: JSON string containing non-sensitive information.

    Raises:
        SkipComponent: When the filter/path does not exist or any exception occurs.
    """
    try:
        filters = get_filters(Specs.awx_manage_check_license_data)
        content = broker[LocalSpecs.awx_manage_check_license_data_raw].content
        if content and filters:
            json_data = json.loads(content[0])
            filter_result = {}
            for item in filters:
                filter_result[item] = json_data.get(item)
            if filter_result:
                return DatasourceProvider(content=json.dumps(collections.OrderedDict(sorted(filter_result.items()))), relative_path='insights_commands/awx-manage_check_license_--data')
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent
