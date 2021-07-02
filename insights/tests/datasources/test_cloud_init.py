import json
import pytest
from mock.mock import Mock

from insights.core.dr import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.datasources.cloud_init import cloud_cfg, LocalSpecs

CLOUD_CFG = """
users:
  - name: demo
    ssh-authorized-keys:
      - key_one
      - key_two

network:
  version: 1
  config:
    - type: physical
      name: eth0
      subnets:
        - type: dhcp
        - type: dhcp6
""".strip()

CLOUD_CFG_NO_NETWORK = """
users:
  - name: demo
    ssh-authorized-keys:
      - key_one
      - key_two
""".strip()

CLOUD_CFG_BAD = """
users
  name -demo
  ssh-authorized-keys
      - key_one
      - key_two
""".strip()


CLOUD_CFG_JSON = {
    'version': 1,
    'config': [
        {
            'type': 'physical',
            'name': 'eth0',
            'subnets': [
                {'type': 'dhcp'},
                {'type': 'dhcp6'}
            ]
        }
    ]
}

RELATIVE_PATH = '/etc/cloud/cloud.cfg'


def test_cloud_cfg():
    cloud_init_file = Mock()
    cloud_init_file.content = CLOUD_CFG.splitlines()
    broker = {LocalSpecs.cloud_cfg_input: cloud_init_file}
    result = cloud_cfg(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=json.dumps(CLOUD_CFG_JSON), relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_cloud_cfg_bad():
    cloud_init_file = Mock()
    cloud_init_file.content = CLOUD_CFG_BAD.splitlines()
    broker = {LocalSpecs.cloud_cfg_input: cloud_init_file}
    with pytest.raises(SkipComponent) as e:
        cloud_cfg(broker)
    assert 'Unexpected exception' in str(e)


def test_cloud_cfg_no_network():
    cloud_init_file = Mock()
    cloud_init_file.content = CLOUD_CFG_NO_NETWORK.splitlines()
    broker = {LocalSpecs.cloud_cfg_input: cloud_init_file}
    with pytest.raises(SkipComponent) as e:
        cloud_cfg(broker)
    assert 'No network section in yaml' in str(e)
