import doctest
from insights.parsers import vmware_tools_conf
from insights.parsers.vmware_tools_conf import VmwareToolsConf
from insights.tests import context_wrap


L3_AGENT_INI = """
[servicediscovery]
disabled=false

[gueststoreupgrade]
poll-interval=3600
""".strip()


def test_vmware_tools_conf():
    result = VmwareToolsConf(context_wrap(L3_AGENT_INI))
    assert result.has_option("servicediscovery", "disabled")
    assert result.get("servicediscovery", "disabled") == "false"
    assert result.get("gueststoreupgrade", "poll-interval") == "3600"


def test_doc():
    env = {"vmware_tools_conf_parser": VmwareToolsConf(context_wrap(L3_AGENT_INI))}
    failed, total = doctest.testmod(vmware_tools_conf, globs=env)
    assert failed == 0
