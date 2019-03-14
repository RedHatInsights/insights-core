"""
TeamdctlConfigDump - command ``teamdctl {team interface} config dump``
======================================================================

This module provides processing for the output of the command
``teamdctl {team interface} config dump``.

Attributes:
    data (dict): Dictionary of keys with values in dict.

Sample configuration file::

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

Examples:
    >>> str(teamdctl_config_dump.device_name)
    'team0'
    >>> str(teamdctl_config_dump.runner_name)
    'activebackup'
    >>> str(teamdctl_config_dump.runner_hwaddr_policy)
    'only_active'
"""

from .. import JSONParser, parser, defaults, CommandParser
from insights.specs import Specs


@parser(Specs.teamdctl_config_dump)
class TeamdctlConfigDump(CommandParser, JSONParser):
    """
    Class to parse the output of ``teamdctl {team interface} config dump``
    """
    @property
    @defaults()
    def device_name(self):
        """
        str: Return the type of the teaming device name
        """
        return self.data.get('device')

    @property
    @defaults()
    def runner_name(self):
        """
        str: Return the type of the teaming runner name
        """
        return self.data.get('runner', {}).get('name')

    @property
    @defaults()
    def runner_hwaddr_policy(self):
        """
        str: Return the type of the teaming runner hwaddr policy
        """
        return self.data.get('runner', {}).get('hwaddr_policy')
