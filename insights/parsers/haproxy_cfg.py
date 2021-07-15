"""
Haproxy configuration files
===========================

Parsers provided by this module are:

HaproxyCfg - file ``/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg`` or ``/etc/haproxy/haproxy.cfg``
---------------------------------------------------------------------------------------------------------------------------
HaproxyCfgScl - file ``/etc/opt/rh/rh-haproxy18/haproxy/haproxy.cfg``
---------------------------------------------------------------------
"""

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs


class HaproxyFile(Parser):
    """
    Base class for ``HaproxyCfg`` and ``HaproxyCfgScl`` classes.

    Attributes:
        data (dict): Dictionary of all parsed sections.
        lines (list): List of all non-commented lines.

    Content of the `haproxy.cfg` file looks like::

        global
            daemon
            group       haproxy
            log         /dev/log local0
            user        haproxy
            maxconn     20480
            pidfile     /var/run/haproxy.pid

        defaults
            retries     3
            maxconn     4096
            log         global
            timeout     http-request 10s
            timeout     queue 1m
            timeout     connect 10s

    Examples:
        >>> type(haproxy)
        <class 'insights.parsers.haproxy_cfg.HaproxyFile'>
        >>> haproxy.data['global']
        {'daemon': '', 'group': 'haproxy', 'log': '/dev/log local0', 'user': 'haproxy', 'maxconn': '20480', 'pidfile': '/var/run/haproxy.pid'}
        >>> haproxy.data['global']['group']
        'haproxy'
        >>> 'global' in haproxy.data
        True
        >>> 'user' in haproxy.data.get('global')
        True
        >>> haproxy.data['defaults']
        {'retries': '3', 'maxconn': '4096', 'log': 'global', 'timeout': ['http-request 10s', 'queue 1m', 'connect 10s']}
    """

    SECTION_NAMES = ("global", "defaults", "frontend", "backend", "listen")

    def __init__(self, context):
        self.data = {}
        self.lines = []
        super(HaproxyFile, self).__init__(context)

    def parse_content(self, content):
        section_dict = {}

        for line in content:
            line = line.strip()
            if line.startswith("#") or line == "":
                continue

            self.lines.append(line)
            split_items = line.split(None, 1)

            # Create a new section, e.g. global: {}
            if split_items[0] in self.SECTION_NAMES:
                section_dict = {}
                section = split_items[0] if len(split_items) == 1 else split_items[0] + " " + split_items[1]
                self.data.update({section: section_dict})
            # Handle attributes inside section
            else:
                if len(split_items) == 1:
                    section_dict[line] = ""
                else:
                    key = split_items[0]
                    value = split_items[1]
                    if key in section_dict:
                        # Convert value into list in case of duplicate key items
                        if not isinstance(section_dict[key], list):
                            section_dict[key] = [section_dict[key]]
                        section_dict[key].append(value)
                    else:
                        section_dict[key] = value


@parser(Specs.haproxy_cfg)
class HaproxyCfg(HaproxyFile):
    """
    Class to parse file ``/var/lib/config-data/puppet-generated/haproxy/etc/haproxy/haproxy.cfg`` or ``haproxy.cfg``.
    """
    pass


@parser(Specs.haproxy_cfg_scl)
class HaproxyCfgScl(HaproxyFile):
    """
    Class to parse file ``/etc/opt/rh/rh-haproxy18/haproxy/haproxy.cfg``.
    """
    pass
