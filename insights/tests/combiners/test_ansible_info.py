from insights.parsers.installed_rpms import InstalledRpms
from insights.combiners import ansible_info
from insights.combiners.ansible_info import (
    AnsibleInfo, ANSIBLE_AUTOMATION_CONTROLLER_PKG, ANSIBLE_CATALOG_WORKER_PKG, ANSIBLE_TOWER_PKG,
    ANSIBLE_AUTOMATION_HUB_PKG)
from insights.tests import context_wrap
import doctest

TOWER_RPM = ANSIBLE_TOWER_PKG + "-1.0.0-1"
AUTO_CONTROLLER_RPM = ANSIBLE_AUTOMATION_CONTROLLER_PKG + "-1.0.1-1"
CATALOG_WORKER_RPM = ANSIBLE_CATALOG_WORKER_PKG + "-1.0.2-1"
HUB_RPM = ANSIBLE_AUTOMATION_HUB_PKG + "-1.0.3-1"
ALL_RPMS = '''
{controller}
{cworker}
{tower}
{hub}
'''.format(
    controller=AUTO_CONTROLLER_RPM,
    cworker=CATALOG_WORKER_RPM,
    tower=TOWER_RPM,
    hub=HUB_RPM).strip()


def test_ansible_info_all():
    rpms = InstalledRpms(context_wrap(ALL_RPMS))
    comb = AnsibleInfo(rpms)
    assert comb is not None
    assert comb.is_tower
    assert comb.tower_version == '1.0.0'
    assert comb[ANSIBLE_TOWER_PKG].nvr == TOWER_RPM
    assert comb[ANSIBLE_AUTOMATION_CONTROLLER_PKG].nvr == AUTO_CONTROLLER_RPM
    assert comb.is_controller
    assert comb.controller_version == '1.0.0'
    assert comb.is_hub
    assert comb.hub_version == '1.0.3'
    assert comb[ANSIBLE_AUTOMATION_HUB_PKG].nvr == HUB_RPM
    assert comb.is_catalog_worker
    assert comb.catalog_worker_version == '1.0.2'
    assert comb[ANSIBLE_CATALOG_WORKER_PKG].nvr == CATALOG_WORKER_RPM


def test_ansible_info_tower():
    rpms = InstalledRpms(context_wrap(TOWER_RPM))
    comb = AnsibleInfo(rpms)
    assert comb.is_tower
    assert comb.is_controller
    assert not comb.is_hub
    assert not comb.is_catalog_worker
    assert comb.tower_version == '1.0.0'
    assert comb.controller_version == '1.0.0'
    assert comb.hub_version is None
    assert comb.catalog_worker_version is None


def test_ansible_info_auto_controller():
    rpms = InstalledRpms(context_wrap(AUTO_CONTROLLER_RPM))
    comb = AnsibleInfo(rpms)
    assert not comb.is_tower
    assert comb.is_controller
    assert not comb.is_hub
    assert not comb.is_catalog_worker
    assert comb.tower_version is None
    assert comb.controller_version == '1.0.1'
    assert comb.hub_version is None
    assert comb.catalog_worker_version is None


def test_ansible_info_docs():
    rpms = InstalledRpms(context_wrap(TOWER_RPM))
    comb = AnsibleInfo(rpms)
    env = {'info': comb}
    failed, total = doctest.testmod(ansible_info, globs=env)
    assert failed == 0
