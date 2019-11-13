"""
SatelliteEnabledFeatures - command ``curl -sk https://localhost:9090/features --connect-timeout 5``
===================================================================================================

The satellite enabled features parser reads the output of
``curl -sk https://localhost:9090/features --connect-timeout 5`` and convert it into a list.
Also it can check if some feature is enabled on this satellite server.

Sample output of ``curl -sk https://localhost:9090/features --connect-timeout 5``::

    ["ansible","dhcp","discovery","dns","dynflow","logs","openscap","pulp","puppet","puppetca","ssh","templates","tftp"]

Examples:

    >>> type(satellite_feature)
    <class 'insights.parsers.satellite_enabled_features.SatelliteEnabledFeatures'>
    >>> enabled_features = ['ansible', 'dhcp', 'discovery', 'dynflow', 'logs', 'openscap', 'pulp', 'puppet', 'puppetca', 'ssh', 'templates', 'tftp']
    >>> satellite_feature == enabled_features
    True
    >>> satellite_feature.is_feature_enabled('dhcp')
    True
    >>> satellite_feature.is_feature_enabled('dns')
    False
"""
from __future__ import unicode_literals

from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.satellite_enabled_features)
class SatelliteEnabledFeatures(CommandParser, list):
    """
    Read the ``curl -sk https://localhost:9090/features --connect-timeout 5`` command and
    convert it to a list.
    """

    def is_feature_enabled(self, feature_name):
        """Check some feature is enabled on this satellite server"""
        return feature_name in self

    def parse_content(self, content):
        for line in content:
            features = line.strip('[]')
            self.extend([feature.strip('"') for feature in features.split(',') if feature])
