"""
CloudCfg - ``/etc/cloud/cloud.cfg``
===================================
Module to parser the content of ``/etc/cloud/cloud.cfg`` file.
"""
from insights import YAMLParser, parser
from insights.specs import Specs


@parser(Specs.cloud_cfg_filtered)
class CloudCfg(YAMLParser):
    """
    This parser parses the ``/etc/cloud/cloud.cfg`` file collected via the
    :mod:`insights.specs.Specs.cloud_cfg_filtered` spec which is the
    filtered per the :mod:`insights.specs.Specs.cloud_cfg` spec into a
    dictionary.

    .. note::
        Since this file may contain sensitive information, it should be
        filtered before the Insights collecting it.  The filters will be added
        via the :mod:`insights.specs.Specs.cloud_cfg` Spec.  When the
        filters is empty, nothing will be parsed.

    The typical content of this file after filtering is (still in Yaml format)::

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
        >>> from insights.core.filters import add_filter
        >>> from insights.specs import Specs
        >>> add_filter(Specs.cloud_cfg, ['network', 'debug', 'ssh_deletekeys'])
        >>> 'users' not in cloud_cfg
        True
        >>> cloud_cfg['network']['version'] == 1
        True
        >>> cloud_cfg['network']['config'] == [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]
        True
    """
    pass
