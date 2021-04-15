"""
SatelliteContentHostsCount - command ``psql -d foreman -c 'select count(*) from hosts'``
========================================================================================

The SatelliteContentHostsCount parser reads the output of
``psql -d foreman -c 'select count(*) from hosts'``.

Sample output of ``psql -d foreman -c 'select count(*) from hosts'``::

     count
    -------
        13
    (1 row)

Examples::

    >>> type(clients)
    <class 'insights.parsers.satellite_content_hosts_count.SatelliteContentHostsCount'>
    >>> clients.count
    13
"""

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.satellite_content_hosts_count)
class SatelliteContentHostsCount(CommandParser):
    """
    Read the ``psql -d foreman -c 'select count(*) from hosts'``
    and set the hosts count to property ``count``.

    Attributes:
        count (int): The count of satellite content hosts
    """

    def parse_content(self, content):
        self.count = None
        if len(content) >= 3 and content[0].strip() == 'count':
            try:
                self.count = int(content[2].strip())
            except ValueError:
                raise ParseException("Unknow satelite content hosts count")
        if self.count is None:
            raise SkipException("Cannot get the count of satellite content hosts")
