"""
NscdConf - file ``/etc/nscd.conf``
==================================

This module parses the contents of the file ``/etc/nscd.conf``.

Each line of the ``nscd.conf`` file specifies either an attribute and a value,
or an attribute, service, and a value. Fields are separated either by SPACE
or TAB characters.  A '#' (number sign) indicates the beginning of a comment;
following characters, up to the end of the line, are not interpreted by nscd.

The function ``service_attributes`` provides information on the lines that
contain a service column such as `passwd` and `group` in the examples below.
The function ``attribute`` can be used to obtain values for attributes not
associated with a service such as `server-user` and `debug-level` in the
examples.

Sample content of the ``nscd.conf`` file looks like::

    #       logfile                 /var/log/nscd.log
    #       threads                 4
    #       max-threads             32
            server-user             nscd
    #       stat-user               somebody
            debug-level             0
    #       reload-count            5
            paranoia                no
    #       restart-interval        3600

            enable-cache            passwd          no
            positive-time-to-live   passwd          600
            negative-time-to-live   passwd          20
            suggested-size          passwd          211
            check-files             passwd          yes
            persistent              passwd          yes
            shared                  passwd          yes
            max-db-size             passwd          33554432
            auto-propagate          passwd          yes

            enable-cache            group           no
            positive-time-to-live   group           3600
            negative-time-to-live   group           60
            suggested-size          group           211
            check-files             group           yes
            persistent              group           yes
            shared                  group           yes
            max-db-size             group           33554432
            auto-propagate          group           yes

Examples:
    >>> conf = shared[NscdConf]
    >>> len([line for line in conf])
    21
    >>> [line for line in conf][0]
    NscdConfLine(attribute='server-user', service=None, value='nscd')
    >>> conf.attribute("server-user")
    'nscd'
    >>> conf.filter("server-user")
    [NscdConfLine(attribute='server-user', service=None, value='nscd')]
    >>> conf.filter("server-user")[0].attribute
    'server-user'
    >>> conf.filter("server-user")[0].value
    'nscd'
    >>> conf.service_attributes("passwd")
    [NscdConfLine(attribute='enable-cache', service='passwd', value='no'),
     NscdConfLine(attribute='positive-time-to-live', service='passwd', value='600'),
     NscdConfLine(attribute='negative-time-to-live', service='passwd', value='20'),
     NscdConfLine(attribute='suggested-size', service='passwd', value='211'),
     NscdConfLine(attribute='check-files', service='passwd', value='yes'),
     NscdConfLine(attribute='persistent', service='passwd', value='yes'),
     NscdConfLine(attribute='shared', service='passwd', value='yes'),
     NscdConfLine(attribute='max-db-size', service='passwd', value='33554432'),
     NscdConfLine(attribute='auto-propagate', service='passwd', value='yes')]
    >>> conf.filter("enable-cache")
    [NscdConfLine(attribute='enable-cache', service='passwd', value='no'),
     NscdConfLine(attribute='enable-cache', service='group', value='no')]
    >>> conf.filter("enable-cache", service="passwd")
    [NscdConfLine(attribute='enable-cache', service='passwd', value='no')]
    >>> conf.filter("enable-cache", service="passwd")[0].attribute
    'enable-cache'
    >>> conf.filter("enable-cache", service="passwd")[0].service
    'passwd'
    >>> conf.filter("enable-cache", service="passwd")[0].value
    'no'
"""
from collections import defaultdict, namedtuple
from .. import Parser, parser, get_active_lines
from insights.specs import Specs

NscdConfLine = namedtuple('NscdConfLine', ['attribute', 'service', 'value'])
"""namedtuple: Represents one line of information from the conf file."""


@parser(Specs.nscd_conf)
class NscdConf(Parser):
    """Class for parsing contents of the ``/etc/nscd.conf`` file."""
    def parse_content(self, content):
        self.data = []
        for line in get_active_lines(content):
            parts = line.split()
            if len(parts) == 2:
                self.data.append(NscdConfLine(parts[0], None, parts[1]))
            else:
                self.data.append(NscdConfLine(parts[0], parts[1], parts[2]))

        self._attributes = {}
        services = defaultdict(list)
        for datum in self.data:
            if datum.service:
                services[datum.service].append(datum)
            else:
                self._attributes[datum.attribute] = datum.value
        self._services = dict(services)

    def service_attributes(self, service_name):
        """list: Returns a list of conf lines matching ``service_name``."""
        return self._services.get(service_name, [])

    def attribute(self, attribute):
        """str: Returns the value of attribute with name ``attribute``.
        Lines that include a ``service`` are not returned by this function.
        """
        return self._attributes.get(attribute)

    def filter(self, attribute, service=None):
        """list: Returns list of conf lines containing ``attribute`` and
        optional ``service`` if present.
        """
        return [conf for conf in self.data
                if attribute in conf.attribute and
                (not service or (service and service in conf.service))]

    def __iter__(self):
        for line in self.data:
            yield line
