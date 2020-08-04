import doctest

from insights.parsers import awx_manage
from insights.parsers.awx_manage import AnsibleTowerLicense
from insights.tests import context_wrap


TRI_LICENSE = """
{"company_name": "", "instance_count": 100, "license_date": 1599364799, "license_key": "********", "subscription_name": "60 Day Evaluation of Red Hat Ansible Automation, Self-Supported (100 Managed Nodes)", "license_type": "enterprise", "trial": true, "valid_key": true, "deployment_id": "ee3fd544f8444c05915607faf3ed2aac7506badb", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 3173549, "grace_period_remaining": 3173549, "compliant": true, "date_warning": false, "date_expired": false, "features": {"activity_streams": true, "ha": true, "ldap": true, "multiple_organizations": true, "surveys": true, "system_tracking": true, "rebranding": true, "enterprise_auth": true, "workflows": true}}
""".strip()

STD_LICENSE = """
{"company_name": "", "instance_count": 100, "license_date": 1641013199, "license_key": "********", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "license_type": "enterprise", "valid_key": true, "deployment_id": "919826a9a40bbded53676b868c74b507c523b370", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 44826976, "trial": false, "grace_period_remaining": 47418976, "compliant": true, "date_warning": false, "date_expired": false, "features": {"activity_streams": true, "ha": true, "ldap": true, "multiple_organizations": true, "surveys": true, "system_tracking": true, "rebranding": true, "enterprise_auth": true, "workflows": true}}
""".strip()



def test_ansible_tower_license():
    ret = AnsibleTowerLicense(context_wrap(TRI_LICENSE))
    assert ret['instance_count'] == 100
    assert ret['license_date'] == 1599364799
    assert ret['features']['ha'] is True
    assert ret['features']['ldap'] is True
    ret = AnsibleTowerLicense(context_wrap(STD_LICENSE))
    assert ret['instance_count'] == 100
    assert ret['license_date'] == 1641013199
    assert ret['features']['ha'] is True
    assert ret['features']['ldap'] is True


def test_awx_manage_doc_examples():
    env = {
        'awx_license': AnsibleTowerLicense(context_wrap(STD_LICENSE)),
    }
    failed, total = doctest.testmod(awx_manage, globs=env)
    assert failed == 0
