#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
