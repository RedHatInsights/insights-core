"""
SatelliteVersionFromClient - command ``curl -k https://satellite.com:port/katello/api/status``
==============================================================================================

The API returns json format of the katello version, the parser parses the
output and return the corresponding satellite version for the satellite client.
"""

from insights.core import JSONParser
from insights.parsers import SkipException
from insights.core.plugins import parser
from insights.specs import Specs


# only list supported satellite versions
KATELLO_SATELLITE_VERSION_MAPPING = {
    '3.14': '6.7',
    '3.16': '6.8',
    '3.18': '6.9'
}


@parser(Specs.get_satellite_version_from_client)
class SatelliteVersionFromClient(JSONParser):
    """
    Parse the output of ``curl -k https://satellite.com:port/katello/api/status``.

    Sample output::

        {"version":"3.18.1.22","timeUTC":"2021-05-20 13:59:20 UTC"}

    Attributes:
        version (string): The satellite version which the client connects to.
        major(int): the major version.
        minor(int): the minor version.

    Examples:
        >>> type(api_output)
        <class 'insights.parsers.satellite_version_from_client.SatelliteVersionFromClient'>
        >>> api_output.version
        '6.9'
        >>> api_output.major
        6
        >>> api_output.minor
        9


    Raises:
        SkipException: When satellite version can not be gotten on client.
    """

    def parse_content(self, content):
        super(SatelliteVersionFromClient, self).parse_content(content)
        self.version = ''
        if 'version' in self.data:
            for key, value in KATELLO_SATELLITE_VERSION_MAPPING.items():
                if self.data.get('version').startswith(key):
                    self.version = value
        if not self.version:
            raise SkipException
        self.major, self.minor = [int(ver) for ver in self.version.split('.')]
