import doctest

from insights.parsers import cni_podman_bridge_conf
from insights.parsers.cni_podman_bridge_conf import CNIPodmanBridgeConf
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check

PODMAN_CNI_FILE = '''
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
'''.strip()


def test_doc_examples():
    env = {
        'cni_podman_bridge_conf': CNIPodmanBridgeConf(context_wrap(PODMAN_CNI_FILE)),
    }
    failed, total = doctest.testmod(cni_podman_bridge_conf, globs=env)
    assert failed == 0


def test_cni_podman_bridge_conf():
    conf = CNIPodmanBridgeConf(context_wrap(PODMAN_CNI_FILE))
    assert len(conf["plugins"]) == 4
    assert conf["plugins"][3]["type"] == "tuning"


def test_cni_podman_bridge_conf_empty():
    assert 'Empty output.' in skip_component_check(CNIPodmanBridgeConf)
