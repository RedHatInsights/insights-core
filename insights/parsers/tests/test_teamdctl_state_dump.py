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

from insights.parsers.teamdctl_state_dump import TeamdctlStateDump
from insights.tests import context_wrap

TEAMDCTL_STATE_DUMP_INFO = """
{
    "runner": {
        "active_port": "eno1"
    },
    "setup": {
        "daemonized": false,
        "dbus_enabled": true,
        "debug_level": 0,
        "kernel_team_mode_name": "activebackup",
        "pid": 4464,
        "pid_file": "/var/run/teamd/team0.pid",
        "runner_name": "activebackup",
        "zmq_enabled": false
    },
    "team_device": {
        "ifinfo": {
            "dev_addr": "2c:59:e5:47:a9:04",
            "dev_addr_len": 6,
            "ifindex": 5,
            "ifname": "team0"
        }
    }
}
""".strip()


TEAMDCTL_STATE_DUMP_INFO_NONE = """
{
    "runner": {
    },
    "setup": {
        "daemonized": false,
        "dbus_enabled": true,
        "debug_level": 0,
        "kernel_team_mode_name": "activebackup",
        "pid": 4464,
        "pid_file": "/var/run/teamd/team0.pid",
        "runner_name": "activebackup",
        "zmq_enabled": false
    },
    "team_device": {
        "ifinfo": {
            "dev_addr": "2c:59:e5:47:a9:04",
            "dev_addr_len": 6,
            "ifindex": 5
        }
    }
}
""".strip()


def test_teamdctl_state_dump():
    result = TeamdctlStateDump(context_wrap(TEAMDCTL_STATE_DUMP_INFO))

    assert result.data == {
        'runner': {
            'active_port': 'eno1'
        },
        'setup': {
            'daemonized': False,
            'zmq_enabled': False,
            'kernel_team_mode_name': 'activebackup',
            'pid': 4464,
            'dbus_enabled': True,
            'debug_level': 0,
            'pid_file': '/var/run/teamd/team0.pid',
            'runner_name': 'activebackup'
        },
        'team_device': {
            'ifinfo': {
                'ifindex': 5,
                'dev_addr': '2c:59:e5:47:a9:04',
                'ifname': 'team0',
                'dev_addr_len': 6}
        }
    }
    assert result['runner']['active_port'] == 'eno1'
    assert result['setup']['runner_name'] == 'activebackup'
    assert result.runner_type == 'activebackup'
    assert result.team_ifname == 'team0'


def test_teamdctl_state_dump_none():
    result = TeamdctlStateDump(context_wrap(TEAMDCTL_STATE_DUMP_INFO_NONE))

    assert result.data == {
        'runner': {
        },
        'setup': {
            'daemonized': False,
            'zmq_enabled': False,
            'kernel_team_mode_name': 'activebackup',
            'pid': 4464,
            'dbus_enabled': True,
            'debug_level': 0,
            'pid_file': '/var/run/teamd/team0.pid',
            'runner_name': 'activebackup'
        },
        'team_device': {
            'ifinfo': {
                'ifindex': 5,
                'dev_addr': '2c:59:e5:47:a9:04',
                'dev_addr_len': 6}
        }
    }
    assert result['setup']['runner_name'] == 'activebackup'
    assert result.runner_type == 'activebackup'
    assert result.team_ifname is None
