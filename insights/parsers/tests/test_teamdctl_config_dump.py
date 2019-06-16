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

from insights.parsers.teamdctl_config_dump import TeamdctlConfigDump
from insights.parsers import teamdctl_config_dump
from insights.tests import context_wrap
import doctest

TEAMDCTL_CONFIG_DUMP_INFO = """
{
    "device": "team0",
    "hwaddr": "DE:5D:21:A8:98:4A",
    "link_watch": [
        {
            "delay_up": 5,
            "name": "ethtool"
        },
        {
            "name": "nsna_ping",
            "target_host ": "target.host"
        }
    ],
    "mcast_rejoin": {
        "count": 1
    },
    "notify_peers": {
        "count": 1
    },
    "runner": {
        "hwaddr_policy": "only_active",
        "name": "activebackup"
    }
}
""".strip()


def test_teamdctl_state_dump():
    result = TeamdctlConfigDump(context_wrap(TEAMDCTL_CONFIG_DUMP_INFO))
    assert result.device_name == 'team0'
    assert result.runner_name == 'activebackup'
    assert result.runner_hwaddr_policy == 'only_active'


def test_nmcli_doc_examples():
    env = {
            'teamdctl_config_dump': TeamdctlConfigDump(context_wrap(TEAMDCTL_CONFIG_DUMP_INFO)),
          }
    failed, total = doctest.testmod(teamdctl_config_dump, globs=env)
    assert failed == 0
