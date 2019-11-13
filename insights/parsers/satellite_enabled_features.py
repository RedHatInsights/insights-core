"""
SatelliteEnabledFeatures - command ``curl -sk https://localhost:9090/features --connect-timeout 5``
===================================================================================================

The satellite enabled features parser reads the output of
``curl -sk https://localhost:9090/features --connect-timeout 5`` and convert it into a list.

Sample output of ``curl -sk https://localhost:9090/features --connect-timeout 5``::

    ["ansible","dhcp","discovery",dynflow","logs","openscap","pulp","puppet","puppetca","ssh","templates","tftp"]

Examples:

    >>> type(satellite_features)
    <class 'insights.parsers.satellite_enabled_features.SatelliteEnabledFeatures'>
    >>> 'dhcp' in satellite_features
    True
    >>> 'dns' in satellite_features
    False
"""

from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.satellite_enabled_features)
class SatelliteEnabledFeatures(CommandParser, list):
    """
    Read the ``curl -sk https://localhost:9090/features --connect-timeout 5`` command and
    convert it to a list.
    """

    def parse_content(self, content):
        for line in content:
            features = line.strip('[]')
            self.extend([feature.strip('"') for feature in features.split(',') if feature])
        if len(self) == 0:
            raise SkipException
