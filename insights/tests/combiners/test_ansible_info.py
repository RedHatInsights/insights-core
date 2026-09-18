from insights.parsers.installed_rpms import InstalledRpms
from insights.combiners import ansible_info
from insights.combiners.ansible_info import (
    AnsibleInfo,
    ANSIBLE_AUTOMATION_CONTROLLER_PKG,
    ANSIBLE_CATALOG_WORKER_PKG,
    ANSIBLE_TOWER_PKG,
    ANSIBLE_AUTOMATION_HUB_PKG,
    ANSIBLE_RECEPTOR_PKG,
    ANSIBLE_RUNNER_PKG,
    ANSIBLE_EDA_CONTROLLER_PKG,
    ANSIBLE_AUTOMATION_GATEWAY_PKG,
)
from insights.tests import context_wrap
import doctest

TOWER_RPM = ANSIBLE_TOWER_PKG + "-1.0.0-1"
AUTO_CONTROLLER_RPM = ANSIBLE_AUTOMATION_CONTROLLER_PKG + "-1.0.1-1"
CATALOG_WORKER_RPM = ANSIBLE_CATALOG_WORKER_PKG + "-1.0.2-1"
HUB_RPM = ANSIBLE_AUTOMATION_HUB_PKG + "-1.0.3-1"
RECEPTOR_RPM = ANSIBLE_RECEPTOR_PKG + "-1.6.6-1"
RUNNER_RPM = ANSIBLE_RUNNER_PKG + "-2.4.2-3"
EDA_CONTROLLER_RPM = ANSIBLE_EDA_CONTROLLER_PKG + "-1.2.3-1"
GATEWAY_RPM = ANSIBLE_AUTOMATION_GATEWAY_PKG + "-2.5.20260422-3"
ALL_RPMS = '''
{controller}
{cworker}
{tower}
{hub}
{receptor}
{runner}
{eda_controller}
{gateway}
'''.format(
    controller=AUTO_CONTROLLER_RPM,
    cworker=CATALOG_WORKER_RPM,
    tower=TOWER_RPM,
    hub=HUB_RPM,
    receptor=RECEPTOR_RPM,
    runner=RUNNER_RPM,
    eda_controller=EDA_CONTROLLER_RPM,
    gateway=GATEWAY_RPM,
).strip()


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
    assert comb.is_receptor
    assert comb.receptor_version == '1.6.6'
    assert comb[ANSIBLE_RECEPTOR_PKG].nvr == RECEPTOR_RPM
    assert comb.is_runner
    assert comb.runner_version == '2.4.2'
    assert comb[ANSIBLE_RUNNER_PKG].nvr == RUNNER_RPM
    assert comb.is_eda_controller
    assert comb.eda_controller_version == '1.2.3'
    assert comb[ANSIBLE_EDA_CONTROLLER_PKG].nvr == EDA_CONTROLLER_RPM
    assert comb.is_gateway
    assert comb.gateway_version == '2.5.20260422'
    assert comb[ANSIBLE_AUTOMATION_GATEWAY_PKG].nvr == GATEWAY_RPM


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
    assert not comb.is_receptor
    assert not comb.is_runner
    assert not comb.is_eda_controller
    assert not comb.is_gateway
    assert comb.receptor_version is None
    assert comb.runner_version is None
    assert comb.eda_controller_version is None
    assert comb.gateway_version is None


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
    assert not comb.is_receptor
    assert not comb.is_runner
    assert not comb.is_eda_controller
    assert not comb.is_gateway
    assert comb.receptor_version is None
    assert comb.runner_version is None
    assert comb.eda_controller_version is None
    assert comb.gateway_version is None


def test_ansible_info_receptor():
    rpms = InstalledRpms(context_wrap(RECEPTOR_RPM))
    comb = AnsibleInfo(rpms)
    assert not comb.is_tower
    assert not comb.is_controller
    assert not comb.is_hub
    assert not comb.is_catalog_worker
    assert comb.is_receptor
    assert not comb.is_runner
    assert not comb.is_eda_controller
    assert not comb.is_gateway
    assert comb.receptor_version == '1.6.6'
    assert comb.tower_version is None
    assert comb.controller_version is None
    assert comb.hub_version is None
    assert comb.catalog_worker_version is None
    assert comb.runner_version is None
    assert comb.eda_controller_version is None
    assert comb.gateway_version is None


def test_ansible_info_runner():
    rpms = InstalledRpms(context_wrap(RUNNER_RPM))
    comb = AnsibleInfo(rpms)
    assert not comb.is_tower
    assert not comb.is_controller
    assert not comb.is_hub
    assert not comb.is_catalog_worker
    assert not comb.is_receptor
    assert comb.is_runner
    assert not comb.is_eda_controller
    assert not comb.is_gateway
    assert comb.runner_version == '2.4.2'
    assert comb.tower_version is None
    assert comb.controller_version is None
    assert comb.hub_version is None
    assert comb.catalog_worker_version is None
    assert comb.receptor_version is None
    assert comb.eda_controller_version is None
    assert comb.gateway_version is None


def test_ansible_info_eda_controller():
    rpms = InstalledRpms(context_wrap(EDA_CONTROLLER_RPM))
    comb = AnsibleInfo(rpms)
    assert not comb.is_tower
    assert not comb.is_controller
    assert not comb.is_hub
    assert not comb.is_catalog_worker
    assert not comb.is_receptor
    assert not comb.is_runner
    assert comb.is_eda_controller
    assert not comb.is_gateway
    assert comb.eda_controller_version == '1.2.3'
    assert comb.tower_version is None
    assert comb.controller_version is None
    assert comb.hub_version is None
    assert comb.catalog_worker_version is None
    assert comb.receptor_version is None
    assert comb.runner_version is None
    assert comb.gateway_version is None


def test_ansible_info_gateway():
    rpms = InstalledRpms(context_wrap(GATEWAY_RPM))
    comb = AnsibleInfo(rpms)
    assert not comb.is_tower
    assert not comb.is_controller
    assert not comb.is_hub
    assert not comb.is_catalog_worker
    assert not comb.is_receptor
    assert not comb.is_runner
    assert not comb.is_eda_controller
    assert comb.is_gateway
    assert comb.gateway_version == '2.5.20260422'
    assert comb.tower_version is None
    assert comb.controller_version is None
    assert comb.hub_version is None
    assert comb.catalog_worker_version is None
    assert comb.receptor_version is None
    assert comb.runner_version is None
    assert comb.eda_controller_version is None


def test_ansible_info_docs():
    rpms = InstalledRpms(context_wrap(TOWER_RPM))
    comb = AnsibleInfo(rpms)
    env = {'info': comb}
    failed, total = doctest.testmod(ansible_info, globs=env)
    assert failed == 0
