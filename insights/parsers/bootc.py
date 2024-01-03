"""
Bootc - Command ``bootc``
=========================
"""
from insights.core import JSONParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.bootc_status)
class BootcStatus(JSONParser):
    """
    Parses the output of command ``bootc status --json``

    Typical output of the command::

        {
            "apiVersion":"org.containers.bootc/v1alpha1",
            "kind":"BootcHost",
            "metadata":{
                "name":"host"
            },
            "spec":{
                "image":{
                    "image":"192.168.124.1:5000/bootc-insights:latest",
                    "transport":"registry"
                }
            },
            "status":{
                "staged":null,
                "booted":{
                    "image":{
                        "image":{
                            "image":"192.168.124.1:5000/bootc-insights:latest",
                            "transport":"registry"
                        },
                        "version":"stream9.20231213.0",
                        "timestamp":null,
                    },
                    "incompatible":false,
                    "pinned":false,
                    "ostree":{
                        "deploySerial":0
                    }
                },
            }
        }

    Examples:
        >>> type(bootc_status)
        <class 'insights.parsers.bootc.BootcStatus'>
        >>> bootc_status['status']['booted']['image']['version'] == 'stream9.20231213.0'
        True
    """
    pass
