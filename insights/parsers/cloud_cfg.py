"""
CloudCfg - ``/etc/cloud/cloud.cfg``
===================================
Module to parser the content of ``/etc/cloud/cloud.cfg`` file. Since this file
may contain sensitive information, it should be filtered before collecting it.
It will be filtered by the filters added to the
`:module:insights.specs.Specs.cloud_cfg` Spec.
"""
from insights import YAMLParser, parser
from insights.specs import Specs


@parser(Specs.cloud_cfg_filtered)
class CloudCfg(YAMLParser):
    """This parser parses the ``/etc/cloud/cloud.cfg`` which is filtered per
    the filters of `:class:insights.specs.Specs.cloud_cfg` into a dictionary.

    The typical content of this file after filtering is in Yaml format:

        debug:
          output: /var/log/cloud-init-debug.log
          verbose: true
        network:
          config:
          - name: eth0
            subnets:
            - type: dhcp
            - type: dhcp6
            type: physical
          version: 1
        ssh_deletekeys: 1

    Attributes:
        data(dict): Cloud-init network configuration.

    Examples:
        >>> cloud_cfg.['network']['version'] == 1
        True
        >>> cloud_cfg.['network']['config'] == [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]
        True
    """
    pass
