import doctest
import pytest

from insights.core import ContentException, ParseException
from insights.parsers import awx_manage, SkipException
from insights.parsers.awx_manage import AnsibleTowerLicenseType, AnsibleTowerLicense, AwxManagePrintSettings
from insights.tests.parsers import skip_exception_check
from insights.tests import context_wrap

GOOD_LICENSE = """
enterprise
""".strip()

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

AWX_MANAGE_PRINT_SETTINGS = '''
{
    "AWX_CLEANUP_PATHS": false,
    "AWX_PROOT_BASE_PATH": "/opt/tmp",
    "INSIGHTS_TRACKING_STATE": true,
    "INSTALL_UUID": "c0d38a6a-4449-4e13-a64b-00e0248ad229",
    "SYSTEM_UUID": "eecfd8dc-5028-46ef-9868-86f7d595da13",
    "TOWER_URL_BASE": "https://10.72.37.79",
    "LOG_AGGREGATOR_ENABLED": true,
    "LOG_AGGREGATOR_LEVEL": "DEBUG"
}
'''.strip()


def test_ansible_tower_license_type():
    ret = AnsibleTowerLicenseType(context_wrap(NO_LICENSE))
    assert ret.type == 'none'
    ret = AnsibleTowerLicenseType(context_wrap(GOOD_LICENSE))
    assert ret.type == 'enterprise'


def test_ansible_tower_license_ab_type():
    with pytest.raises(SkipException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_0))

    with pytest.raises(ContentException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_1))

    with pytest.raises(ParseException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_2))


def test_ansible_tower_license_data():
    ret = AnsibleTowerLicense(context_wrap(AWX_MANAGE_LICENSE))
    assert ret.get("license_type") == 'enterprise'
    assert ret.get("instance_count") == 100
    assert ret.get("time_remaining") == 29885220
    assert ret.get("contact_email") == "test@redhat.com"


def test_ansible_tower_license__data_ab_type():
    assert 'Empty output.' in skip_exception_check(AnsibleTowerLicense)

    with pytest.raises(ContentException):
        AnsibleTowerLicense(context_wrap(NG_COMMAND_1))

    with pytest.raises(ParseException):
        AnsibleTowerLicense(context_wrap(NG_COMMAND_2))

    with pytest.raises(ParseException):
        AnsibleTowerLicense(context_wrap(NO_LICENSE))


def test_awx_manage_print_settings():
    settings = awx_manage.AwxManagePrintSettings(context_wrap(AWX_MANAGE_PRINT_SETTINGS))
    assert not settings['AWX_CLEANUP_PATHS']
    assert settings['INSIGHTS_TRACKING_STATE']
    assert settings['SYSTEM_UUID'] == "eecfd8dc-5028-46ef-9868-86f7d595da13"
    assert settings['LOG_AGGREGATOR_LEVEL'] == "DEBUG"


def test_awx_manage_doc_examples():
    env = {
        'awx_license': AnsibleTowerLicenseType(context_wrap(GOOD_LICENSE)),
        'awx_manage_license': AnsibleTowerLicense(context_wrap(AWX_MANAGE_LICENSE)),
        'settings': AwxManagePrintSettings(context_wrap(AWX_MANAGE_PRINT_SETTINGS))
    }
    failed, total = doctest.testmod(awx_manage, globs=env)
    assert failed == 0
