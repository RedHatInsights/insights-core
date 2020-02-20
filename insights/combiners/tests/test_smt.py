import doctest
import pytest

from insights.combiners import smt
from insights.combiners.smt import CpuTopology
from insights.parsers.smt import CpuCoreOnline, CpuSiblings
from insights.tests import context_wrap


# Path for core online files
ONLINE_PATH = "/sys/devices/system/cpu/cpu{0}/online"
# Path for core siblings files
SIBLINGS_PATH = "/sys/devices/system/cpu/cpu{0}/topology/thread_siblings_list"


@pytest.fixture
def cpu_all_online():
    return [
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(0))),
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(1))),
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(2))),
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(3)))
    ]


def test_hyperthreading_all_online(cpu_all_online):
    siblings = [
        CpuSiblings(context_wrap("0,2", path=SIBLINGS_PATH.format(0))),
        CpuSiblings(context_wrap("1,3", path=SIBLINGS_PATH.format(1))),
        CpuSiblings(context_wrap("0,2", path=SIBLINGS_PATH.format(2))),
        CpuSiblings(context_wrap("1,3", path=SIBLINGS_PATH.format(3)))
    ]

    cpu_topology = CpuTopology(cpu_all_online, siblings)
    assert cpu_topology.online(0)
    assert cpu_topology.siblings(0) == [0, 2]
    assert cpu_topology.online(1)
    assert cpu_topology.siblings(1) == [1, 3]
    assert cpu_topology.online(2)
    assert cpu_topology.siblings(2) == [0, 2]
    assert cpu_topology.online(3)
    assert cpu_topology.siblings(3) == [1, 3]
    assert not cpu_topology.all_solitary


def test_hyperthreading_some_online():
    online = [
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(0))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(1))),
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(2))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(3)))
    ]
    siblings = [
        CpuSiblings(context_wrap("0,2", path=SIBLINGS_PATH.format(0))),
        CpuSiblings(context_wrap("0,2", path=SIBLINGS_PATH.format(2)))
    ]

    cpu_topology = CpuTopology(online, siblings)
    assert cpu_topology.online(0)
    assert cpu_topology.siblings(0) == [0, 2]
    assert not cpu_topology.online(1)
    assert cpu_topology.siblings(1) == []
    assert cpu_topology.online(2)
    assert cpu_topology.siblings(2) == [0, 2]
    assert not cpu_topology.online(3)
    assert cpu_topology.siblings(3) == []
    assert not cpu_topology.all_solitary


def test_without_hyperthreading_all_online(cpu_all_online):
    siblings = [
        CpuSiblings(context_wrap("0", path=SIBLINGS_PATH.format(0))),
        CpuSiblings(context_wrap("1", path=SIBLINGS_PATH.format(1))),
        CpuSiblings(context_wrap("2", path=SIBLINGS_PATH.format(2))),
        CpuSiblings(context_wrap("3", path=SIBLINGS_PATH.format(3)))
    ]

    cpu_topology = CpuTopology(cpu_all_online, siblings)
    assert cpu_topology.online(0)
    assert cpu_topology.siblings(0) == [0]
    assert cpu_topology.online(1)
    assert cpu_topology.siblings(1) == [1]
    assert cpu_topology.online(2)
    assert cpu_topology.siblings(2) == [2]
    assert cpu_topology.online(3)
    assert cpu_topology.siblings(3) == [3]
    assert cpu_topology.all_solitary


def test_without_hyperthreading_some_online():
    online = [
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(0))),
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(1))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(2))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(3)))
    ]
    siblings = [
        CpuSiblings(context_wrap("0", path=SIBLINGS_PATH.format(0))),
        CpuSiblings(context_wrap("1", path=SIBLINGS_PATH.format(1)))
    ]

    cpu_topology = CpuTopology(online, siblings)
    assert cpu_topology.online(0)
    assert cpu_topology.siblings(0) == [0]
    assert cpu_topology.online(1)
    assert cpu_topology.siblings(1) == [1]
    assert not cpu_topology.online(2)
    assert cpu_topology.siblings(2) == []
    assert not cpu_topology.online(3)
    assert cpu_topology.siblings(3) == []
    assert cpu_topology.all_solitary


def test_wrong_index():
    online = [
        CpuCoreOnline(context_wrap("1", path=ONLINE_PATH.format(0))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(1))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(2))),
        CpuCoreOnline(context_wrap("0", path=ONLINE_PATH.format(3)))
    ]
    siblings = [
        CpuSiblings(context_wrap("0", path=SIBLINGS_PATH.format(0))),
    ]

    c = CpuTopology(online, siblings)
    assert c.online(-1) is None
    assert c.siblings(-1) is None
    assert c.online(4) is None
    assert c.siblings(4) is None


def test_doc_examples(cpu_all_online):
    siblings = [
        CpuSiblings(context_wrap("0,2", path=SIBLINGS_PATH.format(0))),
        CpuSiblings(context_wrap("1,3", path=SIBLINGS_PATH.format(1))),
        CpuSiblings(context_wrap("0,2", path=SIBLINGS_PATH.format(2))),
        CpuSiblings(context_wrap("1,3", path=SIBLINGS_PATH.format(3)))
    ]

    env = {
        "cpu_topology": CpuTopology(cpu_all_online, siblings),
    }
    failed, total = doctest.testmod(smt, globs=env)
    assert failed == 0
