import doctest
import pytest

from insights.parsers import awx_manage, SkipException, ParseException
from insights.core import ContentException
from insights.parsers.awx_manage import AnsibleTowerLicenseType
from insights.tests import context_wrap


NO_LICENSE = """
none
""".strip()

STD_LICENSE = """
enterprise
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


def test_ansible_tower_license():
    ret = AnsibleTowerLicenseType(context_wrap(NO_LICENSE))
    assert ret.type == 'none'
    ret = AnsibleTowerLicenseType(context_wrap(STD_LICENSE))
    assert ret.type == 'enterprise'


def test_ansible_tower_license_ab():
    with pytest.raises(SkipException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_0))

    with pytest.raises(ContentException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_1))

    with pytest.raises(ParseException):
        AnsibleTowerLicenseType(context_wrap(NG_COMMAND_2))


def test_awx_manage_doc_examples():
    env = {
        'awx_license': AnsibleTowerLicenseType(context_wrap(STD_LICENSE)),
    }
    failed, total = doctest.testmod(awx_manage, globs=env)
    assert failed == 0
