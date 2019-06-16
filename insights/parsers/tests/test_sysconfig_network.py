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

from insights.parsers.sysconfig import NetworkSysconfig
from insights.tests import context_wrap

NETWORK_SYSCONFIG = """
NETWORKING=yes
HOSTNAME=rhel7-box
GATEWAY=172.31.0.1
NM_BOND_VLAN_ENABLED=no
""".strip()


def test_sysconfig_network():
    result = NetworkSysconfig(context_wrap(NETWORK_SYSCONFIG))
    assert result["GATEWAY"] == '172.31.0.1'
    assert result.get("NETWORKING") == 'yes'
    assert result['NM_BOND_VLAN_ENABLED'] == 'no'
