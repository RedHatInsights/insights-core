import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import net_namespace
from insights.parsers.net_namespace import NetworkNamespace
from insights.tests import context_wrap

LIST_NAMESPACE = """
temp_netns  temp_netns_2  temp_netns_3
""".strip()

LIST_NAMESPACE_2 = """
temp_netns
""".strip()

LIST_NAMESPACE_3 = """
""".strip()

CMD_LIST_NAMESPACE = """
temp_netns_3
temp_netns_2
temp_netns
""".strip()

CMD_LIST_NAMESPACE_2 = """
temp_netns_3
""".strip()

CMD_LIST_NAMESPACE_3 = """
""".strip()


def test_netstat_doc_examples():
    env = {
        'netns_obj': NetworkNamespace(context_wrap(LIST_NAMESPACE))
    }
    failed, total = doctest.testmod(net_namespace, globs=env)
    assert failed == 0


def test_bond_class():
    netns_obj = NetworkNamespace(context_wrap(LIST_NAMESPACE))
    assert netns_obj.netns_list.sort() == ['temp_netns', 'temp_netns_2', 'temp_netns_3'].sort()
    assert len(netns_obj.netns_list) == 3

    netns_obj = NetworkNamespace(context_wrap(LIST_NAMESPACE_2))
    assert netns_obj.netns_list == ['temp_netns']
    assert len(netns_obj.netns_list) == 1

    netns_obj = NetworkNamespace(context_wrap(CMD_LIST_NAMESPACE))
    assert netns_obj.netns_list.sort() == ['temp_netns', 'temp_netns_2', 'temp_netns_3'].sort()
    assert len(netns_obj.netns_list) == 3

    netns_obj = NetworkNamespace(context_wrap(CMD_LIST_NAMESPACE_2))
    assert netns_obj.netns_list == ['temp_netns_3']
    assert len(netns_obj.netns_list) == 1


def test_abnormal():
    with pytest.raises(SkipComponent) as pe:
        NetworkNamespace(context_wrap(LIST_NAMESPACE_3))
    assert "Nothing to parse." in str(pe)

    with pytest.raises(SkipComponent) as pe:
        NetworkNamespace(context_wrap(CMD_LIST_NAMESPACE_3))
    assert "Nothing to parse." in str(pe)
