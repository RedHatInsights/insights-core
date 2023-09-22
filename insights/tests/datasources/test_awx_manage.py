import collections
import json
import pytest

from mock.mock import Mock

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources.awx_manage import LocalSpecs, awx_manage_check_license_data_datasource


AWX_MANAGE_LICENSE = """
{"contact_email": "test@redhat.com", "company_name": "test Inc", "instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "sku": "MCT3691", "support_level": "Standard", "product_name": "Red Hat Ansible Automation Platform", "valid_key": true, "satellite": null, "pool_id": "2c92808179803e530179ea5989a157a4", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}
""".strip()

NG_COMMAND = """
awx-manage: command not found
""".strip()

AWX_MANAGE_FILTER_JSON = {
    "license_type": "enterprise",
    "time_remaining": 29885220,
    "instance_count": 100,
    "support_level": "Standard"
}

RELATIVE_PATH = 'insights_commands/awx-manage_check_license_--data'


def setup_function(func):
    if Specs.awx_manage_check_license_data in filters._CACHE:
        del filters._CACHE[Specs.awx_manage_check_license_data]
    if Specs.awx_manage_check_license_data in filters.FILTERS:
        del filters.FILTERS[Specs.awx_manage_check_license_data]

    if func is test_ansible_tower_license_datasource or func is test_ansible_tower_license_datasource_NG_output:
        filters.add_filter(Specs.awx_manage_check_license_data, ["license_type", "support_level", "instance_count", "time_remaining"])
    if func is test_ansible_tower_license_datasource_no_filter:
        filters.add_filter(Specs.awx_manage_check_license_data, [])


def test_ansible_tower_license_datasource():
    awx_manage_data = Mock()
    awx_manage_data.content = AWX_MANAGE_LICENSE.splitlines()
    broker = {LocalSpecs.awx_manage_check_license_data_raw: awx_manage_data}
    result = awx_manage_check_license_data_datasource(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=json.dumps(collections.OrderedDict(sorted(AWX_MANAGE_FILTER_JSON.items()))), relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_ansible_tower_license_datasource_no_filter():
    awx_manage_data = Mock()
    awx_manage_data.content = AWX_MANAGE_LICENSE.splitlines()
    broker = {LocalSpecs.awx_manage_check_license_data_raw: awx_manage_data}
    with pytest.raises(SkipComponent) as e:
        awx_manage_check_license_data_datasource(broker)
    assert 'SkipComponent' in str(e)


def test_ansible_tower_license_datasource_NG_output():
    awx_manage_data = Mock()
    awx_manage_data.content = NG_COMMAND.splitlines()
    broker = {LocalSpecs.awx_manage_check_license_data_raw: awx_manage_data}
    with pytest.raises(SkipComponent) as e:
        awx_manage_check_license_data_datasource(broker)
    assert 'Unexpected exception' in str(e)
