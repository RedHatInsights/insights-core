"""
AwxManage - commands ``awx-manage``
===================================

Parsers contains in this module are:

AnsibleTowerLicenseType - command ``awx-manage check_license``
--------------------------------------------------------------
"""

from insights import JSONParser, parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs
import json


@parser(Specs.awx_manage_check_license)
class AnsibleTowerLicenseType(CommandParser, JSONParser):
    """
    Parses the output of command  ``awx-manage check_license``
    NOTE: This class is deprecated, consider to use class AnsibleTowerLicense

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
        data = json.loads(content[0])
        self.type = data.get("license_type")


@parser(Specs.awx_manage_check_license)
class AnsibleTowerLicense(CommandParser, JSONParser):
    """
    Parses the output of command  ``awx-manage check_license``

    Sample output of the command::

        enterprise

    Attributes:
        type (str): The license type, e.g. "enterprise"

    Examples:
    >>> type(awx_manage_license)
    <class 'insights.parsers.awx_manage.AnsibleTowerLicense'>
    >>> awx_manage_license.data['license_type'] == "enterprise"
    True
    >>> awx_manage_license.data['time_remaining']
    29885220
    """
    pass
