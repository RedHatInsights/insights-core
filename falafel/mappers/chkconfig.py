"""
chkconfig - command
===================
"""
from collections import namedtuple
from .. import Mapper, mapper
import re


@mapper('chkconfig')
class ChkConfig(Mapper):
    """
    A mapper for working with data gathered from `chkconfig` utility.

    Sample input data is shown as `content` in the examples below.

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
        self.parsed_lines = {}
        """dict: Dictionary of content lines access by service name."""
        self.level_states = {}
        """dict: Dictionary of set of level numbers access by service name."""

        super(ChkConfig, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Mapper context content
        """

        # sysv services are in the form "service     0:off"
        # while xinetd services are "service:    off"
        on_state = re.compile(r':\s*on(?:\s+|$)')
        off_state = re.compile(r':\s*off(?:\s+|$)')

        valid_states = [on_state, off_state]
        for line in content:
            if any(state.search(line) for state in valid_states):
                # xinetd service names have a trailing colon ("telnet:  on")
                service = line.split()[0].strip(' \t:')
                enabled = on_state.search(line) is not None
                self.services[service] = enabled
                self.parsed_lines[service] = line

                states = []
                # Register the state of this service at each runlevel by
                # parsing e.g. "0:off 1:off 2:on" etc.
                for level in line.split()[1:]:
                    # xinetd services have no runlevels, so set their states
                    # to those of xinetd if they are on, else all off
                    if len(level.split(':')) < 2:
                        if enabled:
                            # This may except if xinetd isn't in services,
                            # but xinetd services are only reported by
                            # chkconfig when it's on.
                            states = self.level_states['xinetd']
                        else:
                            # Disabled xinetd services are effectively
                            # off at every runlevel
                            states = ['0:off','1:off','2:off','3:off',
                                      '4:off','5:off','6:off']
                        continue
                    num, state = level.split(':')
                    states.append(self.LevelState(num.strip(), state.strip()))
                self.level_states[service] = states

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
            raise KeyError("Service {} not in Chkconfig".format(service_name))

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
