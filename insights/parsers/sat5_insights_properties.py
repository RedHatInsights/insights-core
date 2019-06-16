#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
