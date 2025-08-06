import pytest
import yaml

from collections import defaultdict
from mock.mock import Mock

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs
from insights.specs.datasources.cloud_init import LocalSpecs, cloud_cfg


CLOUD_CFG = """
users:
  - name: demo
    ssh-authorized-keys:
      - key_one
      - key_two
    passwd: $6$j212wezy$7H/1LT4f9/N3wpgNunhsIqtMj62OKiS3nyNwuizouQc3u7MbYCarYeAHWYPYb2FT.lbioDm2RrkJPb9BZMN1O/

ssh_deletekeys: {value}

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


CLOUD_CFG_FILTERED = """
network:
  config:
  - name: eth0
    subnets:
    - type: dhcp
    - type: dhcp6
    type: physical
  version: 1
ssh_deletekeys: 1
"""

RELATIVE_PATH = '/etc/cloud/cloud.cfg'


def setup_function(func):
    if func is test_cloud_cfg:
        filters.add_filter(Specs.cloud_cfg, ['ssh_deletekeys', 'network', 'debug'])
    if func is test_cloud_cfg_no_filter:
        filters.add_filter(Specs.cloud_cfg, [])
    elif func is test_cloud_cfg_bad:
        filters.add_filter(Specs.cloud_cfg, ['not_found'])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(set)


@pytest.mark.parametrize("ssh_deletekeys", [0, 1])
def test_cloud_cfg(ssh_deletekeys):
    cloud_cfg_string = CLOUD_CFG.format(value=ssh_deletekeys)
    cloud_cfg_dict = yaml.safe_load(CLOUD_CFG_FILTERED)
    cloud_cfg_dict["ssh_deletekeys"] = ssh_deletekeys

    cloud_init_file = Mock()
    cloud_init_file.content = cloud_cfg_string.splitlines()
    broker = {LocalSpecs.cloud_cfg_input: cloud_init_file}
    result = cloud_cfg(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=yaml.dump(cloud_cfg_dict), relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_cloud_cfg_no_filter():
    cloud_init_file = Mock()
    cloud_init_file.content = CLOUD_CFG.format(value=1).splitlines()
    broker = {LocalSpecs.cloud_cfg_input: cloud_init_file}
    with pytest.raises(SkipComponent) as e:
        cloud_cfg(broker)
    assert 'SkipComponent' in str(e)


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
