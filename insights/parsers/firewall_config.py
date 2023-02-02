"""
FirewallDConf - file ``/etc/firewalld/firewalld.conf``
======================================================

The FirewallDConf class parses the file ``/etc/firewalld/firewalld.conf``.
And returns a dict contains the firewall configurations.

Examples:

    >>> type(firewalld)
    <class 'insights.parsers.firewall_config.FirewallDConf'>
    >>> 'DefaultZone' in firewalld
    True
    >>> firewalld['DefaultZone']
    'public'
"""
from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.firewalld_conf)
class FirewallDConf(Parser, dict):
    """
    Class for parsing ``/etc/firewalld/firewalld.conf`` file.
    """

    def parse_content(self, content):
        self.update(split_kv_pairs(content, use_partition=False))
        if not self:
            raise SkipComponent("empty content")
