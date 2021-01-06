"""
AwxManage - commands ``awx-manage``
===================================

Parsers contains in this module are:

AnsibleTowerLicenseType - command ``awx-manage check_license``
--------------------------------------------------------------
"""

from insights import JSONParser, parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.awx_manage_check_license)
class AnsibleTowerLicenseType(CommandParser, JSONParser):
    """
    Parses the output of command  ``awx-manage check_license``

    Sample output of the command::

        enterprise

    Attributes:
        type (str): The license type, e.g. "enterprise"

    Examples:
    >>> type(awx_license)
    <class 'insights.parsers.awx_manage.AnsibleTowerLicenseType'>
    >>> awx_license.type == "enterprise"
    True
    """
    def parse_content(self, content):
        if not content:
            raise SkipException
        if len(content) != 1:
            raise ParseException("Invalid output: {0}".format(content))
        self.type = content[0].strip()
