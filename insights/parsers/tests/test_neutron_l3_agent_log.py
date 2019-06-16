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

import doctest
from insights.parsers import neutron_l3_agent_log
from insights.parsers.neutron_l3_agent_log import NeutronL3AgentLog
from insights.tests import context_wrap

from datetime import datetime

AGENT_LOG = """
2017-09-17 10:05:06.241 141544 INFO neutron.agent.l3.ha [-] Router 01d51830-0e3e-4100-a891-efd7dbc000b1 transitioned to backup
2017-09-17 10:05:07.828 141544 WARNING neutron.agent.linux.iptables_manager [-] Duplicate iptables rule detected. This may indicate a bug in the the iptables rule generation code. Line: -A neutron-l3-agent-INPUT -p tcp -m tcp --dport 9697 -j DROP
2017-09-17 10:05:07.829 141544 WARNING neutron.agent.linux.iptables_manager [-] Duplicate iptables rule detected. This may indicate a bug in the the iptables rule generation code. Line: -A neutron-l3-agent-INPUT -m mark --mark 0x1/0xffff -j ACCEP
"""


def test_metrics_log():
    log = NeutronL3AgentLog(context_wrap(AGENT_LOG))
    assert len(log.get('INFO')) == 1
    assert 'Duplicate iptables rule detected' in log
    assert len(log.get('Duplicate iptables rule detected')) == 2
    assert len(list(log.get_after(datetime(2017, 2, 17, 19, 36, 38)))) == 3


def test_doc():
    env = {'agent_log': NeutronL3AgentLog(context_wrap(AGENT_LOG, path='/var/log/neutron/l3-agent.log'))}
    failed, total = doctest.testmod(neutron_l3_agent_log, globs=env)
    assert failed == 0
