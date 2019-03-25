from insights.parsers import SkipException
from insights.parsers import ip_netns_exec_namespace_lsof
from insights.parsers.ip_netns_exec_namespace_lsof import IpNetnsExecNamespaceLsofI
from insights.tests import context_wrap
import doctest
import pytest


IP_NETNS_EXEC_NAMESPACE_LSOF_I = """
COMMAND   PID   USER    FD  TYPE  DEVICE     SIZE/OFF  NODE NAME
neutron-n 975   root    5u  IPv4  6482691    0t0        TCP *:http (LISTEN)
""".strip()

EXCEPTION1 = """
""".strip()

EXCEPTION2 = """
COMMAND     PID   USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
""".strip()


def test_ip_netns_exec_namespace_lsof():
    data = IpNetnsExecNamespaceLsofI(context_wrap(IP_NETNS_EXEC_NAMESPACE_LSOF_I))
    assert len(data.search(node="TCP")) == 1
    assert len(data.search(command="neutron-n")) == 1
    assert len(data.search(user="nobody")) == 0
    assert data.data[0]["command"] == "neutron-n"
    assert data.data[0].get("node") == "TCP"
    assert [ps[2] for ps in data] == ["root"]


def test_ip_netns_exec_namespace_lsof_documentation():
    env = {
        "ns_lsof": IpNetnsExecNamespaceLsofI(context_wrap(IP_NETNS_EXEC_NAMESPACE_LSOF_I)),
    }
    failed, total = doctest.testmod(ip_netns_exec_namespace_lsof, globs=env)
    assert failed == 0


def test_ip_netns_exec_namespace_lsof_exception1():
    with pytest.raises(SkipException) as e:
        IpNetnsExecNamespaceLsofI(context_wrap(EXCEPTION1))
    assert "Empty file" in str(e)


def test_ip_netns_exec_namespace_lsof_exception2():
    with pytest.raises(SkipException) as e:
        IpNetnsExecNamespaceLsofI(context_wrap(EXCEPTION2))
    assert "Useless data" in str(e)
