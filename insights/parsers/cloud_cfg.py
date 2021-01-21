"""
CloudCfg - datasource ``cloud_cfg``
===================================
"""
from insights import JSONParser, parser
from insights.specs import Specs


@parser(Specs.cloud_cfg)
class CloudCfg(JSONParser):
    """This parser parses the output of ``cloud_cfg`` datasource.

    Typical output from the datasource is::

        {"version": 1, "config": [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]}

    Attributes:

        data(dict): Cloud-init network configuration.

    Examples:
        >>> cloud_cfg.data['version'] == 1
        True
        >>> cloud_cfg.data['config'] == [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]
        True
"""
    pass
