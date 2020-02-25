"""
CloudInitCustomeNetwork - file ``/etc/cloud/cloud.cfg.d/99-custom-networking.cfg``
==================================================================================

This module provides parsing for cloudinit custom networking configuration file.
``CloudInitCustomNetworking`` is a parser for ``/etc/cloud/cloud.cfg.d/99-custom-networking.cfg`` files.

Typical output is::

    network:
      version: 1
      config:
      - type: physical
        name: eth0
        subnets:
          - type: dhcp
          - type: dhcp6

Examples:
    >>> cloud_init_custom_network_config.data['network']['config'][0]['name']
    'eth0'
    >>> cloud_init_custom_network_config.data['network']['config'][0]['subnets'][0]['type'] == 'dhcp'
    True
    >>> cloud_init_custom_network_config.data['network']['config'][0]['subnets'][1]['type'] == 'dhcp6'
    True
"""


from insights import YAMLParser, parser
from insights.specs import Specs


@parser(Specs.cloud_init_custom_network)
class CloudInitCustomNetworking(YAMLParser):
    """ Class for parsing the content of ``/etc/cloud/cloud.cfg.d/99-custom-networking.cfg``."""
    pass
