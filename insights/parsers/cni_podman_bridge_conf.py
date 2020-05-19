"""
CNIPodmanBridgeConf - file ``/etc/cni/net.d/87-podman-bridge.conflist``
=======================================================================

This parser converts file ``/etc/cni/net.d/87-podman-bridge.conflist``
into a dictionary that matches the JSON string in the file.

Sample file content::

    {
        "cniVersion": "0.4.0",
        "name": "podman",
        "plugins": [
            {
                "type": "bridge",
                "bridge": "cni-podman0",
                "isGateway": true,
                "ipMasq": true,
                "ipam": {
                    "type": "host-local",
                    "routes": [
                        {
                            "dst": "0.0.0.0/0"
                        }
                    ],
                    "ranges": [
                        [
                            {
                                "subnet": "10.12.0.0/16",
                                "gateway": "10.12.0.1"
                            }
                        ]
                    ]
                }
            },
            {
                "type": "portmap",
                "capabilities": {
                    "portMappings": true
                }
            },
            {
                "type": "firewall",
                "backend": "iptables"
            },
            {
                "type": "tuning"
            }
        ]
    }

    Examples:
    >>> len(cni_podman_bridge_conf["plugins"])
    4
    >>> cni_podman_bridge_conf["plugins"][0]["ipMasq"]
    True
"""

from insights.specs import Specs
from insights import JSONParser, parser


@parser(Specs.cni_podman_bridge_conf)
class CNIPodmanBridgeConf(JSONParser):
    """
    Class for file: /etc/cni/net.d/87-podman-bridge.conflist
    """
    pass
