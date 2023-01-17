import doctest

from insights.parsers import cloud_cfg
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


CONFIG_1 = """
{"ssh_deletekeys": 1, "network": {"config": "disabled"}}
"""

CONFIG_2 = """
{"ssh_deletekeys": 1, "network": {"version": 1, "config": [{"type": "physical", "name": "eth0", "subnets": [{"type": "dhcp"}, {"type": "dhcp6"}]}]}, "debug": {"output": "/var/log/cloud-init-debug.log", "verbose": true}}
"""


def test_cloud_cfg():
    result = cloud_cfg.CloudCfg(context_wrap(CONFIG_1))
    assert result.data['network'] == {'config': 'disabled'}

    result = cloud_cfg.CloudCfg(context_wrap(CONFIG_2))
    assert result.data['network']['config'][0]['name'] == 'eth0'


def test_cloud_cfg_empty():
    assert 'There is no data' in skip_component_check(cloud_cfg.CloudCfg)


def test_doc_examples():
    env = {
        'cloud_cfg': cloud_cfg.CloudCfg(context_wrap(CONFIG_2)),
    }
    failed, total = doctest.testmod(cloud_cfg, globs=env)
    assert failed == 0
