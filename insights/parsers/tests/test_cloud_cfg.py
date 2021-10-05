import doctest

from insights.parsers import cloud_cfg
from insights.parsers.tests import skip_exception_check
from insights.tests import context_wrap


CONFIG_1 = """
{"users": [{"name": "demo", "ssh-authorized-keys": ["key_one", "key_two"], "passwd": "$6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/"}], "network": {"config": "disabled"}, "system_info": {"default_user": {"name": "user2", "plain_text_passwd": "someP@assword", "home": "/home/user2"}}}
"""

CONFIG_2 = """
{"users": [{"name": "demo", "ssh-authorized-keys": ["key_one", "key_two"], "passwd": "$6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/"}], "network": {"version": 1, "config": [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]}, "system_info": {"default_user": {"name": "user2", "plain_text_passwd": "someP@assword", "home": "/home/user2"}}, "debug": {"output": "/var/log/cloud-init-debug.log", "verbose": true}}
"""


def test_cloud_cfg():
    result = cloud_cfg.CloudCfg(context_wrap(CONFIG_1))
    assert result.data['network'] == {'config': 'disabled'}

    result = cloud_cfg.CloudCfg(context_wrap(CONFIG_2))
    assert result.data['network']['config'][0]['name'] == 'eth0'


def test_cloud_cfg_empty():
    assert 'Empty output.' in skip_exception_check(cloud_cfg.CloudCfg)


def test_doc_examples():
    env = {
        'cloud_cfg': cloud_cfg.CloudCfg(context_wrap(CONFIG_2)),
    }
    failed, total = doctest.testmod(cloud_cfg, globs=env)
    assert failed == 0
