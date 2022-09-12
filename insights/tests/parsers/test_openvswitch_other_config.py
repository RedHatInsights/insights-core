from insights.parsers.openvswitch_other_config import OpenvSwitchOtherConfig
from insights.tests import context_wrap

other_config_1 = """
{dpdk-init="true", dpdk-lcore-mask="30000003000", dpdk-socket-mem="4096,4096", pmd-cpu-mask="30000003000"}
""".strip()

other_config_2 = """
{dpdk-init="true", dpdk-lcore-mask="c00000c00", dpdk-socket-mem="4096,4096", pmd-cpu-mask="c00000c00"}
""".strip()

other_config_3 = """
{}
""".strip()

other_config_4 = """
{pmd-cpu-mask="3000000000030030030"}
""".strip()

other_config_5 = """
ovs-vsctl: unix:/var/run/openvswitch/db.sock: database connection failed (Permission denied)
""".strip()


def test_openvswitch_():
    result = OpenvSwitchOtherConfig(context_wrap(other_config_1))
    assert "pmd-cpu-mask" in result
    assert result.get("dpdk-init") == "true"
    assert result.get("dpdk-socket-mem") == "4096,4096"
    assert result.get("pmd-cpu-mask") == "30000003000"
    assert result.get("dpdk-lcore-mask") == "30000003000"
    assert result["dpdk-lcore-mask"] == "30000003000"

    result = OpenvSwitchOtherConfig(context_wrap(other_config_2))
    assert result.get("dpdk-init") == "true"
    assert result.get("dpdk-socket-mem") == "4096,4096"
    assert result.get("pmd-cpu-mask") == "c00000c00"

    result = OpenvSwitchOtherConfig(context_wrap(other_config_3))
    assert result.get("dpdk-init") is None

    result = OpenvSwitchOtherConfig(context_wrap(other_config_4))
    assert result.get("dpdk-init") is None
    assert result.get("pmd-cpu-mask") == "3000000000030030030"

    result = OpenvSwitchOtherConfig(context_wrap(other_config_5))
    assert result.get("dpdk-init") is None
