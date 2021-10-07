import doctest

from insights.parsers import cloud_cfg
from insights.parsers.tests import skip_exception_check
from insights.tests import context_wrap


CONFIG_1 = """
{"users": [{"name": "", "ssh-authorized-keys": ["key_one", "key_two"], "passwd": ""}], "ssh_deletekeys": 1, "network": {"config": "disabled"}, "system_info": {"default_user": {"name": "", "plain_text_passwd": "", "home": ""}}}
"""

CONFIG_2 = """
{"users": [{"name": "", "ssh-authorized-keys": ["key_one", "key_two"], "passwd": ""}], "ssh_deletekeys": 1, "network": {"version": 1, "config": [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]}, "system_info": {"default_user": {"name": "", "plain_text_passwd": "", "home": ""}}, "debug": {"output": "/var/log/cloud-init-debug.log", "verbose": true}}
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
