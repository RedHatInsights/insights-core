from insights.parsers import cloud_init_custom_network
from insights.parsers.cloud_init_custom_network import CloudInitCustomNetworking
from insights.tests import context_wrap
import doctest

CLOUD_INIT_CONFIG = """
network:
    version: 1
    config:
    - type: physical
      name: eth0
      subnets:
        - type: dhcp
        - type: dhcp6
"""


def test_cloud_init_custom_network():
    result = cloud_init_custom_network.CloudInitCustomNetworking(context_wrap(CLOUD_INIT_CONFIG))
    assert result.data['network']['config'][0]['name'] == 'eth0'
    assert result.data['network']['config'][0]['subnets'][0]['type'] == 'dhcp'
    assert result.data['network']['config'][0]['subnets'][1]['type'] == 'dhcp6'


def test_cloud_init_custom_networks_doc_examples():
    env = {
        'cloud_init_custom_network_config': CloudInitCustomNetworking(context_wrap(CLOUD_INIT_CONFIG)),
    }
    failed, total = doctest.testmod(cloud_init_custom_network, globs=env)
    assert failed == 0
