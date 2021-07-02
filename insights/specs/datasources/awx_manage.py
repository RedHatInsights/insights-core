"""
Custom datasources for awx_manage information
"""
import json

from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by awx_manage datasources """

    awx_manage_check_license_data_raw = simple_command("/usr/bin/awx-manage check_license --data")
    """ Returns the output of command ``/usr/bin/awx-manage check_license --data``  """


@datasource(LocalSpecs.awx_manage_check_license_data_raw, HostContext)
def awx_manage_check_license_data(broker):
    """
    This datasource provides the not-sensitive information collected
    from ``/usr/bin/awx-manage check_license --data``.

    Typical content of ``/usr/bin/awx-manage check_license --data`` file is::

        {"contact_email": "test@redhat.com", "company_name": "test Inc", "instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "sku": "MCT3691", "support_level": "Standard", "product_name": "Red Hat Ansible Automation Platform", "valid_key": true, "satellite": null, "pool_id": "2c92808179803e530179ea5989a157a4", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}

    Returns:
        str: JSON string containing non-sensitive information.

    Raises:
        SkipComponent: When the path does not exist or any exception occurs.
    """
    try:
        content = broker[LocalSpecs.awx_manage_check_license_data_raw].content
        if content:
            json_data = json.load(content)
            filter_result = {}
            filter_keys = [
                "subscription_name", "date_expired", "valid_key", "support_level", "current_instances", "instance_count",
                "free_instances", "time_remaining", "available_instances", "grace_period_remaining", "trial", "date_warning",
                "license_type", "compliant", "license_date", "product_name"
            ]
            for item in filter_keys:
                filter_result[item] = json_data.get(item)
            return DatasourceProvider(content=json.dumps(filter_result))
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
