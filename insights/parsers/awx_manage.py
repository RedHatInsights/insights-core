"""
AwxManage - commands ``awx-manage``
===================================

Parsers contains in this module are:

AnsibleTowerLicense - command ``awx-manage check_license --data``
-----------------------------------------------------------------
"""

from insights import JSONParser, parser
from insights.specs import Specs


@parser(Specs.awx_manage_check_license)
class AnsibleTowerLicense(JSONParser):
    """
    Parses the output of command  ``awx-manage check_license --data``

    Sample output of the command::

        {"company_name": "", "instance_count": 100, "license_date": 1641013199,
         "license_key": "********", "license_type": "enterprise",
         "subscription_name": "Red Hat Ansible Automation, Standard (100 Managed Nodes)",
         "valid_key": true, "current_instances": 1, "available_instances": 100,
         "free_instances": 99, "time_remaining": 44826976, "trial": false,
         "grace_period_remaining": 47418976,
         "deployment_id": "919826a9a40bbded53676b868c74b507c523b370",
         "compliant": true, "date_warning": false, "date_expired": false,
         "features": {"activity_streams": true, "ha": true, "ldap": true,
                      "multiple_organizations": true,
                      "surveys": true, "system_tracking": true,
                      "rebranding": true, "enterprise_auth": true,
                      "workflows": true}
        }

    Examples:

    >>> type(awx_license)
    <class 'insights.parsers.awx_manage.AnsibleTowerLicense'>
    >>> awx_license['valid_key']
    True
    >>> awx_license['license_type'] == "enterprise"
    True
    >>> awx_license['time_remaining']
    44826976
    >>> awx_license['date_expired']
    False
    >>> awx_license['trial']
    False
    """
    pass
