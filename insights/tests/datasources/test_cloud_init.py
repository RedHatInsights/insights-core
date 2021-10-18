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
    passwd: $6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/

ssh_deletekeys: 1

network:
  version: 1
  config:
    - type: physical
      name: eth0
      subnets:
        - type: dhcp
        - type: dhcp6
""".strip()

CLOUD_CFG_BAD_INDENT = """
#cloud-config
users:
  - name: demo
    ssh-authorized-keys:
      - key_one
      - key_two
    passwd: $6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/

ssh_deletekeys: 1

network:
  config: disabled

 system_info:
   default_user:
    name: user2
    plain_text_passwd: 'someP@assword'
    home: /home/user2
""".strip()

CLOUD_CFG_BAD = """
users
  name -demo
  ssh-authorized-keys
      - key_one
      - key_two
""".strip()


CLOUD_CFG_JSON = {
    "users": "",
    "ssh_deletekeys": 1,
    "network": {
        "version": 1,
        "config": [
            {
                "type": "physical",
                "name": "eth0",
                "subnets": [
                    {
                        "type": "dhcp"
                    },
                    {
                        "type": "dhcp6"
                    }
                ]
            }
        ]
    }
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
    assert 'Invalid YAML format' in str(e)

    cloud_init_file.content = CLOUD_CFG_BAD_INDENT.splitlines()
    broker = {LocalSpecs.cloud_cfg_input: cloud_init_file}
    with pytest.raises(SkipComponent) as e:
        cloud_cfg(broker)
    assert 'Unexpected exception' in str(e)
