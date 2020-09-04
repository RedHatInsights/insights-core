"""
IpsecConf parser - file ``/etc/ipsec.conf``
===========================================

IpsecConf parser the file /etc/ipsec.conf about
the configuration and control information
for the Libreswan IPsec subsystem.
"""

from collections import defaultdict

from insights.specs import Specs
from insights.core import CommandParser
from .. import parser, get_active_lines
from insights.parsers import SkipException


@parser(Specs.ipsec_conf)
class IpsecConf(CommandParser, dict):
    """
    Class for parsing the file ``/etc/ipsec.conf`` about the configuration
    and control information for the Libreswan IPsec subsystem

    Raises:
        SkipException: When content is empty or cannot be parsed.

    Sample output of this command is::

        # /etc/ipsec.conf - Libreswan IPsec configuration file
        #
        # see 'man ipsec.conf' and 'man pluto' for more information
        #
        # For example configurations and documentation, see https://libreswan.org/wiki/

        config setup
                # plutodebug="control parsing"
                # plutodebug="all crypt"
                plutodebug=none
                # It seems that T-Mobile in the US and Rogers/Fido in Canada are
                # using 25/8 as "private" address space on their wireless networks.
                # This range has never been announced via BGP (at least up to 2015)
                virtual_private=%v4:10.0.0.0/8,%v4:192.168.0.0/16,%v4:172.16.0.0/12,%v4:25.0.0.0/8,%v4:100.64.0.0/10,%v6:fd00::/8,%v6:fe80::/10

        # if it exists, include system wide crypto-policy defaults
        include /etc/crypto-policies/back-ends/libreswan.config

        # It is best to add your IPsec connections as separate files in /etc/ipsec.d/
        include /etc/ipsec.d/*.conf

    Examples:
        >>> ipsec_conf['config']['setup']['plutodebug'] == 'none'
        True
        >>> ipsec_conf['include']
        ['/etc/crypto-policies/back-ends/libreswan.config', '/etc/ipsec.d/*.conf']
    """

    def parse_content(self, content):
        if not content:
            raise SkipException('No content.')

        ipsec_type, ipsec_name = "", ""
        ipsec_sections = {}

        try:
            for line in get_active_lines(content):
                if line.startswith('include '):
                    include, path = [field.strip() for field in line.split()]
                    array = self.get('include', [])
                    array.append(path)
                    self['include'] = array
                    continue

                if line.startswith(('conn ', 'config ')):
                    ipsec_type, ipsec_name = [field.strip() for field in line.split()]
                    ipsec_sections = self.get(ipsec_type, defaultdict(dict))
                    continue

                if '=' not in line or ipsec_type == "" or ipsec_name == "":
                    # skip the options that don't within a section
                    continue

                key, value = [field.strip() for field in line.split('=')]
                ipsec_sections[ipsec_name][key] = value
                self[ipsec_type] = ipsec_sections

        except ValueError:
            raise SkipException('Syntax error')
