"""
snmpd configuration files
=========================

Parsers provided by this module are:

SnmpdConf - file ``/etc/snmp/snmpd.conf``
-----------------------------------------
"""

from insights.core import Parser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers import get_active_lines
from insights.core.exceptions import ParseException


@parser(Specs.snmpd_conf)
class SnmpdConf(Parser, dict):
    """
    Class for parsing the file ``/etc/snmp/snmpd.conf``

    Sample file content::

        #       sec.name  source          community
        com2sec notConfigUser  default       public

        #       groupName      securityModel securityName
        group   notConfigGroup v1           notConfigUser
        group   notConfigGroup v2c           notConfigUser

        # Make at least  snmpwalk -v 1 localhost -c public system fast again.
        #       name           incl/excl     subtree         mask(optional)
        view    systemview    included   .1.3.6.1.2.1.1
        view    systemview    included   .1.3.6.1.2.1.25.1.1

        #       group          context sec.model sec.level prefix read   write  notif
        access  notConfigGroup ""      any       noauth    exact  systemview none none

        dontLogTCPWrappersConnects yes
        include_ifmib_iface_prefix eth enp1s0

    Examples:
        >>> type(snmpd_conf)
        <class 'insights.parsers.snmpd_conf.SnmpdConf'>
        >>> snmpd_conf['dontLogTCPWrappersConnects']
        ['yes']
        >>> snmpd_conf['include_ifmib_iface_prefix']
        ['eth enp1s0']
    """

    def parse_content(self, content):
        if not content:
            raise ParseException('Empty Content')

        for line in get_active_lines(content):
            k, v = [i.strip() for i in line.split(None, 1)]
            if k not in self:
                self[k] = []
            self[k].append(v)
