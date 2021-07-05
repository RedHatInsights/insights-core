import doctest
import pytest

from insights.parsers import awx_manage, SkipException
from insights.core import ContentException
from insights.core import filters
from insights.specs import Specs
from insights.parsers.awx_manage import AnsibleTowerLicenseType, AnsibleTowerLicense
from insights.tests import context_wrap


NO_LICENSE = """
none
""".strip()

NG_COMMAND_0 = ""

NG_COMMAND_1 = """
awx-manage: command not found
""".strip()

NG_COMMAND_2 = """
Traceback (most recent call last):
File \"/bin/awx-manage\", line 11, in <module>
    load_entry_point('awx==3.6.4', 'console_scripts', 'awx-manage')()
""".strip()

AWX_MANAGE_LICENSE = """
{"contact_email": "test@redhat.com", "company_name": "test Inc", "instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "sku": "MCT3691", "support_level": "Standard", "product_name": "Red Hat Ansible Automation Platform", "valid_key": true, "satellite": null, "pool_id": "2c92808179803e530179ea5989a157a4", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}
""".strip()


def setup_function(func):
    if Specs.awx_manage_check_license in filters._CACHE:
        del filters._CACHE[Specs.awx_manage_check_license]
    if Specs.awx_manage_check_license in filters.FILTERS:
        del filters.FILTERS[Specs.awx_manage_check_license]

    if func is test_ansible_tower_license or func is test_ansible_tower_license_type:
        filters.add_filter(Specs.awx_manage_check_license, ["license_type", "support_level", "instance_count", "time_remaining"])


def test_ansible_tower_license_type():
    ret = AnsibleTowerLicenseType(context_wrap(AWX_MANAGE_LICENSE))
    assert ret.type == 'enterprise'


def test_ansible_tower_license_ab_type():
    with pytest.raises(SkipException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_0))

    with pytest.raises(ContentException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_1))

    with pytest.raises(ValueError):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_2))

    with pytest.raises(ValueError):
        AnsibleTowerLicenseType(context_wrap(NO_LICENSE))


def test_ansible_tower_license():
    ret = AnsibleTowerLicense(context_wrap(AWX_MANAGE_LICENSE))
    assert ret.get("license_type") == 'enterprise'
    assert ret.get("instance_count") == 100
    assert ret.get("time_remaining") == 29885220
    assert ret.get("contact_email") == "test@redhat.com"


def test_awx_manage_doc_examples():
    env = {
        'awx_license': AnsibleTowerLicenseType(context_wrap(AWX_MANAGE_LICENSE)),
        'awx_manage_license': AnsibleTowerLicense(context_wrap(AWX_MANAGE_LICENSE)),
    }
    failed, total = doctest.testmod(awx_manage, globs=env)
    assert failed == 0
