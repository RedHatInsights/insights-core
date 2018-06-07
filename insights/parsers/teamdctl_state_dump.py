"""
TeamdctlStateDump - command ``teamdctl {team interface} state dump``
====================================================================

This module provides processing for the output of the command
``teamdctl {team interface} state dump`` which is JSON pattern.

Examples:

    >>> teamdctl_state_dump_content = '''
    ... {
    ...     "runner": {
    ...         "active_port": "eno1"
    ...     },
    ...     "setup": {
    ...         "daemonized": false,
    ...         "dbus_enabled": true,
    ...         "debug_level": 0,
    ...         "kernel_team_mode_name": "activebackup",
    ...         "pid": 4464,
    ...         "pid_file": "/var/run/teamd/team0.pid",
    ...         "runner_name": "activebackup",
    ...         "zmq_enabled": false
    ...     },
    ...     "team_device": {
    ...         "ifinfo": {
    ...             "dev_addr": "2c:59:e5:47:a9:04",
    ...             "dev_addr_len": 6,
    ...             "ifindex": 5,
    ...             "ifname": "team0"
    ...         }
    ...     }
    ... }
    ... '''.strip()

    >>> from insights.parsers.teamdctl_state_dump import TeamdctlStateDump
    >>> from insights.tests import context_wrap
    >>> shared = {TeamdctlStateDump: TeamdctlStateDump(context_wrap(teamdctl_state_dump_content))}
    >>> result = shared[TeamdctlStateDump]
    >>> result['runner']['active_port']
    'eno1'
    >>> result.runner_type
    'activebackup'
    >>> result.team_ifname
    'team0'
"""

from .. import JSONParser, parser, defaults, CommandParser
from insights.specs import Specs


@parser(Specs.teamdctl_state_dump)
class TeamdctlStateDump(CommandParser, JSONParser):
    """
    Class to parse the output of ``teamdctl {team interface} state dump``.
    """
    @property
    @defaults()
    def runner_type(self):
        """
        str: Return the type of the teaming runner
        """
        return self.data["setup"]["runner_name"]

    @property
    @defaults()
    def team_ifname(self):
        """
        str: Return the teaming device name
        """
        return self.data["team_device"]["ifinfo"]["ifname"]
