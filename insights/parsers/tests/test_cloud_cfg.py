import doctest
from insights.parsers import cloud_cfg
from insights.tests import context_wrap


CONFIG_1 = """
{"config": "disabled"}
"""

CONFIG_2 = """
{"version": 1, "config": [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]}
"""


def test_cloud_cfg():
    result = cloud_cfg.CloudCfg(context_wrap(CONFIG_1))
    assert result.data['config'] == 'disabled'

    result = cloud_cfg.CloudCfg(context_wrap(CONFIG_2))
    assert result.data['config'][0]['name'] == 'eth0'


def test_doc_examples():
    env = {
        'cloud_cfg': cloud_cfg.CloudCfg(context_wrap(CONFIG_2)),
    }
    failed, total = doctest.testmod(cloud_cfg, globs=env)
    assert failed == 0
