"""
AwxManage - commands ``awx-manage``
===================================

Parsers contains in this module are:

AnsibleTowerLicenseType - command ``/usr/bin/awx-manage check_license``

AnsibleTowerLicense - command ``/usr/bin/awx-manage check_license --data``
--------------------------------------------------------------------------
"""

from insights import JSONParser, parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


@parser(Specs.awx_manage_check_license)
class AnsibleTowerLicenseType(CommandParser, JSONParser):
    """
    Parses the output of command  ``/usr/bin/awx-manage check_license``

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


@parser(Specs.awx_manage_check_license_data)
class AnsibleTowerLicense(CommandParser, JSONParser):
    """
    Parses the output of command  ``/usr/bin/awx-manage check_license --data``

    Sample output of the command::

        {"instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "support_level": "Standard", "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}

    Examples:
        >>> type(awx_manage_license)
        <class 'insights.parsers.awx_manage.AnsibleTowerLicense'>
        >>> awx_manage_license.data['license_type'] == "enterprise"
        True
        >>> awx_manage_license.data['time_remaining']
        29885220
    """
    pass
