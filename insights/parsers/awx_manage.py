"""
AwxManage - commands ``awx-manage``
===================================

Parsers contains in this module are:

AnsibleTowerLicense - command ``awx-manage check_license``
----------------------------------------------------------
"""

from insights import JSONParser, parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs
from insights.util import deprecated
import json


@parser(Specs.awx_manage_check_license)
class AnsibleTowerLicenseType(CommandParser, JSONParser):
    """
    Parses the output of command  ``awx-manage check_license``
    .. note::
        This class is deprecated, consider to use class AnsibleTowerLicense

    Sample output of the command::

       {"contact_email": "test@redhat.com", "company_name": "test Inc", "instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "sku": "MCT3691", "support_level": "Standard", "product_name": "Red Hat Ansible Automation Platform", "valid_key": true, "satellite": null, "pool_id": "2c92808179803e530179ea5989a157a4", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}

    Examples:
    >>> type(awx_license)
    <class 'insights.parsers.awx_manage.AnsibleTowerLicenseType'>
    >>> awx_license.type == "enterprise"
    True
    """
    def __init__(self, *args, **kwargs):
        deprecated(AnsibleTowerLicenseType, "Use AnsibleTowerLicense in insights.insights.awx_manage instead.")
        super(AnsibleTowerLicenseType, self).__init__(*args, **kwargs)

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

        {"contact_email": "test@redhat.com", "company_name": "test Inc", "instance_count": 100, "license_date": 1655092799, "license_type": "enterprise", "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)", "sku": "MCT3691", "support_level": "Standard", "product_name": "Red Hat Ansible Automation Platform", "valid_key": true, "satellite": null, "pool_id": "2c92808179803e530179ea5989a157a4", "current_instances": 1, "available_instances": 100, "free_instances": 99, "time_remaining": 29885220, "trial": false, "grace_period_remaining": 32477220, "compliant": true, "date_warning": false, "date_expired": false}

    Examples:
    >>> type(awx_manage_license)
    <class 'insights.parsers.awx_manage.AnsibleTowerLicense'>
    >>> awx_manage_license.data['license_type'] == "enterprise"
    True
    >>> awx_manage_license.data['time_remaining']
    29885220
    """
    pass
