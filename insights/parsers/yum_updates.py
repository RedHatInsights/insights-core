"""
YumUpdates - parser for the `yum_updates` datasource
====================================================
Provides a list of available package updates, along with related advisories. This information
is collected using DNF/YUM python interface.
"""

from insights import JSONParser, parser
from insights.specs import Specs


@parser(Specs.yum_updates)
class YumUpdates(JSONParser):
    """
    Expected output of the command is::

        {
          "releasever": "8",
          "basearch": "x86_64",
          "update_list": {
            "NetworkManager-1:1.22.8-4.el8.x86_64": {
              "available_updates": [
                {
                  "package": "NetworkManager-1:1.22.8-5.el8_2.x86_64",
                  "repository": "rhel-8-for-x86_64-baseos-rpms",
                  "basearch": "x86_64",
                  "releasever": "8",
                  "erratum": "RHSA-2020:3011"
                }
              ]
            }
          },
          "metadata_time": "2021-01-01T09:39:45Z"
        }

    Examples:
        >>> len(updates.updates)
        1
        >>> updates.updates['NetworkManager-1:1.22.8-4.el8.x86_64']['available_updates'][0] == { \
        'basearch': 'x86_64', \
        'erratum': 'RHSA-2020:3011', \
        'package': 'NetworkManager-1:1.22.8-5.el8_2.x86_64', \
        'releasever': '8', \
        'repository': 'rhel-8-for-x86_64-baseos-rpms'}
        True
    """

    @property
    def updates(self):
        """
        Returns:
            dict: Dict(package name -> list of available updates)
        """
        return self.data['update_list']
