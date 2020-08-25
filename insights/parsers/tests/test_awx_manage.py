import doctest

from insights.parsers import awx_manage
from insights.parsers.awx_manage import AnsibleTowerLicense
from insights.tests import context_wrap


NO_LICENSE = """
none

""".strip()

STD_LICENSE = """
enterprise
""".strip()


def test_ansible_tower_license():
    ret = AnsibleTowerLicense(context_wrap(NO_LICENSE))
    assert ret.type == 'none'
    ret = AnsibleTowerLicense(context_wrap(STD_LICENSE))
    assert ret.type == 'enterprise'


def test_awx_manage_doc_examples():
    env = {
        'awx_license': AnsibleTowerLicense(context_wrap(STD_LICENSE)),
    }
    failed, total = doctest.testmod(awx_manage, globs=env)
    assert failed == 0
