"""
Sat5InsightsProperties - File ``redhat-access-insights.properties``
===================================================================
"""
from insights import Parser, LegacyItemAccess, parser, get_active_lines
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.sat5_insights_properties)
class Sat5InsightsProperties(LegacyItemAccess, Parser):
    """
    Class to parse configuration file
    ``/etc/redhat-access/redhat-access-insights.properties`` on Satellite 5
    Server.

    The typical content is::

        portalurl = https://cert-api.access.redhat.com/r/insights
        enabled = true
        debug = true
        rpmname = redhat-access-insights

    Examples:
        >>> insights_props.enabled
        True
        >>> insights_props['debug']
        'true'
        >>> insights_props['rpmname']
        'redhat-access-insights'

    Attributes:
        enabled (bool): True when insights is enabled on the Satellite 5.
                        Otherwise, False

    Raises:
        SkipException: When file content is empty.
    """
    def parse_content(self, content):
        if not content:
            raise SkipException('Empty content.')

        self.data = {}
        for line in get_active_lines(content):
            key, value = [l.strip() for l in line.split('=', 1)]
            self.data[key] = value
        self.enabled = self.get('enabled') == 'true'
