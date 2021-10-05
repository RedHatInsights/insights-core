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

        {"users": [{"name": "demo", "ssh-authorized-keys": ["key_one", "key_two"], "passwd": "$6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/"}], "network": {"version": 1, "config": [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]}, "system_info": {"default_user": {"name": "user2", "plain_text_passwd": "someP@assword", "home": "/home/user2"}}, "debug": {"output": "/var/log/cloud-init-debug.log", "verbose": true}}

    Attributes:

        data(dict): Cloud-init network configuration.

    Examples:
        >>> cloud_cfg.data['network']['version'] == 1
        True
        >>> cloud_cfg.data['network']['config'] == [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]
        True
"""
    pass
