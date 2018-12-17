"""
IfCFGStaticRoute - files ``/etc/sysconfig/network-scripts/route-*``
===================================================================

IfCFGStaticRoute is a parser for the static route network interface
definition files in ``/etc/sysconfig/network-scripts``.
"""

from .. import parser, LegacyItemAccess, Parser
from insights.specs import Specs


@parser(Specs.ifcfg_static_route)
class IfCFGStaticRoute(LegacyItemAccess, Parser):
    """
    IfCFGStaticRoute is a parser for the static route network interface
    definition files in ``/etc/sysconfig/network-scripts``.  These are
    pulled into the network scripts using ``source``, so they are mainly
    ``bash`` environment declarations of the form **KEY=value**.  These
    are stored in the ``data`` property as a dictionary.  Quotes surrounding
    the value

    Because this parser reads multiple files, the interfaces are stored as a
    list within the parser and need to be iterated through in order to find
    specific interfaces.

    Sample configuration from a static connection in file ``/etc/sysconfig/network-scripts/rute-test-net``::

        ADDRESS0=10.65.223.0
        NETMASK0=255.255.254.0
        GATEWAY0=10.65.223.1

    Examples:

        >>> type(conn_info)
        <class 'insights.parsers.ifcfg_static_route.IfCFGStaticRoute'>
        >>> conn_info.static_route
        'test-net'
        >>> conn_info.data['ADDRESS0']
        '10.65.223.0'
        >>> import pprint
        >>> conn_details = pprint.pprint(conn_info.data)
        >>> conn_details
        {'ADDRESS0': '10.65.223.0', 'NETMASK0': '255.255.254.0', 'GATEWAY0': '10.65.223.1'}

    """
    def __init__(self, context):
        self.data = {}
        self.static_route = context.path.split("network-scripts/route-", 1)[1]
        super(IfCFGStaticRoute, self).__init__(context)

    def parse_content(self, content):
        for line in content:
            key, value = line.split("=", 1)
            self.data[key] = value

    @property
    def static_route_connection(self):
        """(list): List of all static route devices"""
        return self.data[self.static_route]
