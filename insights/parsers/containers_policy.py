"""
ContainersPolicy - file ``/etc/containers/policy.json``
=======================================================
"""
from insights import JSONParser, parser
from insights.specs import Specs


@parser(Specs.containers_policy)
class ContainersPolicy(JSONParser):
    """
    Class for converting file ``/etc/containers/policy.json``
    into a dictionary that matches the JSON string in the file.

    Sample file content::

        {
          "default": [
            {
              "type": "insecureAcceptAnything"
            }
          ],
          "transports": {
            "docker": {
              "registry.access.redhat.com": [
                {
                  "type": "signedBy",
                  "keyType": "GPGKeys",
                  "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
                }
              ],
              "registry.redhat.io/redhat/redhat-operator-index": [
                {
                  "type": "insecureAcceptAnything"
                }
              ],
              "registry.redhat.io": [
                {
                  "type": "signedBy",
                  "keyType": "GPGKeys",
                  "keyPath": "/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
                }
              ]
            },
            "docker-daemon": {
              "": [
                {
                  "type": "insecureAcceptAnything"
                }
              ]
            }
          }
        }

    Examples:
        >>> len(containers_policy["default"])
        1
    """
    pass
