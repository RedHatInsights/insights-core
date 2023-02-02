"""
ChkConfig - command ``chkconfig``
=================================
"""
import re

from collections import namedtuple

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.chkconfig)
class ChkConfig(CommandParser):
    """
    A parser for working with data gathered from `chkconfig` utility.

    Sample input data is shown as `content` in the examples below.

    Raises:
        SkipComponent: When nothing is parsed.

    Examples:
        >>> content = '''
        ... auditd         0:off   1:off   2:on    3:on    4:on    5:on    6:off
        ... crond          0:off   1:off   2:on    3:on    4:on    5:on    6:off
        ... iptables       0:off   1:off   2:on    3:on    4:on    5:on    6:off
        ... kdump          0:off   1:off   2:off   3:on    4:on    5:on    6:off
        ... restorecond    0:off   1:off   2:off   3:off   4:off   5:off   6:off
        ... xinetd:        0:off   1:off   2:on    3:on    4:on    5:on    6:off
        ...         rexec:         off
        ...         rlogin:        off
        ...         rsh:           off
        ...         telnet:        on
        ... '''
        >>> shared[ChkConfig].is_on('crond')
        True
        >>> shared[ChkConfig].is_on('httpd')
        False
        >>> shared[ChkConfig].is_on('rexec')
        False
        >>> shared[ChkConfig].is_on('telnet')
        True
        >>> shared[ChkConfig].parsed_lines['crond']
        'crond          0:off   1:off   2:on    3:on    4:on    5:on    6:off'
        >>> shared[ChkConfig].parsed_lines['telnet']
        '        telnet:        on'
        >>> shared[ChkConfig].levels_on('crond')
        set(['3', '2', '5', '4'])
        >>> shared[ChkConfig].levels_off('crond')
        set(['1', '0', '6'])
        >>> shared[ChkConfig].levels_on('telnet')
        set([])
        >>> shared[ChkConfig].levels_off('telnet')
        set([])
    """

    LevelState = namedtuple('LevelState', ['level', 'state'])
    """namedtuple: Represents the state of a particular service level."""

    def __init__(self, *args, **kwargs):
        self.services = {}
        """dict: Dictionary of bool indicating if service is enabled,
        access by service name ."""
        self.service_list = []
        """list: List of service names in order of appearance."""
        self.parsed_lines = {}
        """dict: Dictionary of content lines access by service name."""
        self.level_states = {}
        """dict: Dictionary of set of level numbers access by service name."""

        super(ChkConfig, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content
        """

        # sysv services are in the form "service     0:off"
        # while xinetd services are "service:    off"
        state_re = re.compile(r':\s*(?P<state>on|off)(?:\s+|$)')

        for line in content:
            if state_re.search(line):
                # xinetd service names have a trailing colon ("telnet:  on")
                service = line.split()[0].strip(' \t:')
                # Note that for regular services this assumes the ':on' occurs
                # in the current run level.  It does not check the run level.
                # enabled = on_state.search(line) is not None
                enabled = ':on' in line or line.endswith('on')
                self.services[service] = enabled
                self.parsed_lines[service] = line
                self.service_list.append(service)

                states = []
                # Register the state of this service at each runlevel by
                # parsing e.g. "0:off 1:off 2:on" etc.
                for level in line.split()[1:]:
                    # xinetd services have no runlevels, so set their states
                    # to those of xinetd if they are on, else all off
                    if len(level.split(':')) < 2:
                        if enabled:
                            if 'xinetd' in self.level_states:
                                # A xinetd-based service is only on for the
                                # SysV run states that xinetd itself is on.
                                states = self.level_states['xinetd']
                            else:
                                # RHEL 7.3 'chkconfig' is actually faked up
                                # by systemd, and doesn't list xinetd as a
                                # service.  Run levels are meaningless here,
                                # so we list 'on' for all SysV run levels.
                                states = [self.LevelState(str(x), 'on')
                                          for x in range(7)]
                        else:
                            # Disabled xinetd services are effectively
                            # off at every runlevel
                            states = [self.LevelState(str(x), 'off')
                                      for x in range(7)]
                        continue
                    num, state = level.split(':')
                    states.append(self.LevelState(num.strip(), state.strip()))
                self.level_states[service] = states

        if not self.services:
            raise SkipComponent

    def is_on(self, service_name):
        """
        Checks if the service is enabled in chkconfig.

        Args:
            service_name (str): service name

        Returns:
            bool: True if service is enabled, False otherwise
        """
        return self.services.get(service_name, False)

    def _level_check(self, service_name, state):
        if service_name in self.parsed_lines:
            return set([l.level
                        for l in self.level_states[service_name]
                        if l.state == state])
        else:
            raise KeyError("Service {0} not in Chkconfig".format(service_name))

    def levels_on(self, service_name):
        """set (str): Returns set of level numbers where `service_name` is `on`.

        Raises:
            KeyError: Raises exception if `service_name` is not in Chkconfig.
        """
        return self._level_check(service_name, state='on')

    def levels_off(self, service_name):
        """set (str): Returns set of levels where `service_name` is `off`.

        Raises:
            KeyError: Raises exception if `service_name` is not in Chkconfig.
        """
        return self._level_check(service_name, state='off')
