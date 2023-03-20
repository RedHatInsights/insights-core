import doctest

from insights.parsers import teamdctl_config_dump
from insights.parsers.teamdctl_config_dump import TeamdctlConfigDump
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check

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


def test_teamdctl_state_dump_empty():
    assert 'Empty output.' in skip_component_check(TeamdctlConfigDump)


def test_nmcli_doc_examples():
    env = {
            'teamdctl_config_dump': TeamdctlConfigDump(context_wrap(TEAMDCTL_CONFIG_DUMP_INFO)),
          }
    failed, total = doctest.testmod(teamdctl_config_dump, globs=env)
    assert failed == 0
