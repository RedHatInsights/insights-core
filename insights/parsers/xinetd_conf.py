"""
XinetdConf - files ``/etc/xinetd.conf`` and in ``/etc/xinetd.d/``
=================================================================

This module provides parsing for the ``/etc/xinetd.conf`` and
``/etc/xinetd.d/*`` files.

Sample input data of file ``/etc/xinetd.conf`` looks like::

    defaults
    {
            enabled                 =
            no_access               = 0.0.0.0/0
            instances               = 60
            per_source              = 128
            log_type                = SYSLOG authpriv
            log_on_success	    = HOST PID DURATION EXIT
            log_on_failure	    = HOST
            cps                     = 25 30
            max_load                = 2
    }

    includedir /etc/xinetd.d

Sample input data of file ``/etc/xinetd.d/tftp`` looks like::

    service tftp
    {
            socket_type             = dgram
            protocol                = udp
            wait                    = yes
            user                    = root
            server                  = /usr/sbin/in.tftpd
            server_args             = -s /var/lib/tftpboot
            disable                 = yes
            per_source              = 11
            cps                     = 100 2
            flags                   = IPv4
    }

Examples:

    >>> xinetd_conf = shared[XinetdConf].data
    >>> assert xinetd_conf.get('is_valid') == True
    >>> assert xinetd_conf.get('is_includedir') == True
    >>> xinetd_conf.get('is_includedir')
    '/etc/xinetd.d'
    >>> 'defaults' in xinetd_conf
    True
    >>> xinetd_conf.get('defaults')
    {   'enabled': '',
        'v6only': 'no',
        'log_on_failure': 'HOST',
        'umask': '002',
        'log_on_success': 'PID HOST DURATION EXIT',
        'instances': '50',
        'per_source': '10',
        'groups': 'yes',
        'cps': '50 10',
        'log_type': 'SYSLOG daemon info'
    }
    >>> 'tftp' in xinetd_conf
    True
    >>> xinetd_conf.get('tftp')
    {	'protocol': 'udp',
        'socket_type': 'dgram',
        'server': '/usr/sbin/in.tftpd',
        'server_args': '-s /var/lib/tftpboot',
        'disable': 'yes',
        'flags': 'IPv4',
        'user': 'root',
        'per_source': '11',
        'cps': '100 2',
        'wait': 'yes'
    }
    >>> 'abc' in xinetd_conf
    False
    >>> xinetd_conf.get('abc')
    >>>
    >>>
    >>> XINETD_CONF_BAD = '''
    ... defaults {
    ...         umask           = 002
    ... }
    ...
    ... includedir /etc/xinetd.d
    ... '''
    >>> xinetd_conf = shared[XinetdConf].data
    >>> assert xinetd_conf.get('is_valid') == False
    >>> 'defaults' in xinetd_conf
    False

"""

from .. import LegacyItemAccess, Parser, parser, get_active_lines
from insights.specs import Specs


@parser(Specs.xinetd_conf)
class XinetdConf(LegacyItemAccess, Parser):
    """Parse contents of file ``/etc/xinetd.conf`` and ``/etc/xinetd.d/*``."""
    def parse_content(self, content):
        self.data = {}
        self.is_valid = True
        section = None
        for line in get_active_lines(content):

            if "{" == line:
                section_con = {}

            elif "}" == line:
                self.data[section] = section_con
                section = None

            elif "includedir" in line:
                self.data["includedir"] = line.split(None, 1)[-1]

            elif not section and "defaults" == line:
                section = line
            elif not section and "service" in line:
                section = line.split(None, 1)[-1]

            elif "=" in line:
                key, _, value = line.partition("=")
                section_con[key.strip()] = value.strip()

            else:
                self.is_valid = False
                break
        self.is_includedir = '/etc/xinetd.d' == self.data.get('includedir')
