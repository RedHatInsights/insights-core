import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import smt
from insights.parsers.smt import CpuSMTActive, CpuSMTControl, CpuCoreOnline, CpuSiblings
from insights.tests import context_wrap


@pytest.mark.parametrize("setting, on", [
    ("0", False),
    ("1", True)
])
def test_cpu_smt_active(setting, on):
    p = CpuSMTActive(context_wrap(setting))
    assert p.on == on


@pytest.mark.parametrize("setting, on, modifiable, supported", [
    ("on", True, True, True),
    ("off", False, True, True),
    ("forceoff", False, False, True),
    ("notsupported", False, False, False)
])
def test_cpu_smt_control(setting, on, modifiable, supported):
    p = CpuSMTControl(context_wrap(setting))
    assert p.on == on
    assert p.modifiable == modifiable
    assert p.supported == supported


@pytest.mark.parametrize("setting, on, status", [
    (0, False, "Offline"),
    (1, True, "Online")
])
def test_cpu_core_online(setting, on, status):
    path = "/sys/devices/system/cpu/cpu{0}/online"

    p = CpuCoreOnline(context_wrap(str(setting), path=path.format(setting)))
    assert p.core_id == setting
    assert p.on == on
    assert repr(p) == "[Core {0}: {1}]".format(setting, status)


@pytest.mark.parametrize("setting, core_id, siblings", [
    ("0,2", 0, [0, 2]),
    ("1-3", 3, [1, 2, 3]),
    ("1", 1, [1])
])
def test_cpu_siblings(setting, core_id, siblings):
    path = "/sys/devices/system/cpu/cpu{0}/topology/thread_siblings_list"

    p = CpuSiblings(context_wrap(setting, path=path.format(core_id)))
    assert p.core_id == core_id
    assert p.siblings == siblings
    assert repr(p) == "[Core {0} Siblings: {1}]".format(core_id, siblings)


@pytest.mark.parametrize("parser", [
    CpuSMTActive,
    CpuSMTControl,
    CpuCoreOnline,
    CpuSiblings
])
def test_exceptions(parser):
    with pytest.raises(SkipComponent):
        parser(context_wrap(""))


def test_doc_examples():
    path_cpu_core_online = "/sys/devices/system/cpu/cpu0/online"
    path_cpu_siblings = "/sys/devices/system/cpu/cpu0/topology/thread_siblings_list"

    env = {
        "cpu_smt_active": CpuSMTActive(context_wrap("1")),
        "cpu_smt_control": CpuSMTControl(context_wrap("off")),
        "cpu_core_online": CpuCoreOnline(context_wrap("1", path=path_cpu_core_online)),
        "cpu_siblings": CpuSiblings(context_wrap("0,2", path=path_cpu_siblings)),
    }
    failed, total = doctest.testmod(smt, globs=env)
    assert failed == 0
