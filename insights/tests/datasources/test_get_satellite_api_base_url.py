import pytest

from insights.core.dr import SkipComponent
from insights.parsers.rhsm_conf import RHSMConf
from insights.tests import context_wrap
from insights.specs.datasources.get_satellite_api_base_url import base_url_of_satellite_api

RHSM_CONF = """
[server]
# Server hostname:
hostname = vm-abc.def.ghs.com

# Server prefix:
prefix = /rhsm

# Server port:
port = 8443

# Set to 1 to disable certificate validation:
insecure = 0

# Set the depth of certs which should be checked
# when validating a certificate
ssl_verify_depth = 3
""".strip()

RHSM_CONF_WITHOUT_HOSTNAME = """
[server]
# Server prefix:
prefix = /rhsm

# Server port:
port = 8443

# Set to 1 to disable certificate validation:
insecure = 0

# Set the depth of certs which should be checked
# when validating a certificate
ssl_verify_depth = 3
""".strip()

RHSM_CONF_WITHOUT_PORT = """
[server]
# Server hostname:
hostname = vm-abc.def.ghs.com
# Server prefix:
prefix = /rhsm

# Set to 1 to disable certificate validation:
insecure = 0

# Set the depth of certs which should be checked
# when validating a certificate
ssl_verify_depth = 3
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


def test_api_url():
    rhsm_parser = RHSMConf(context_wrap(RHSM_CONF))
    broker = {RHSMConf: rhsm_parser}
    result = base_url_of_satellite_api(broker)
    assert result is not None
    assert result == 'https://vm-abc.def.ghs.com:8443'


def test_rhsm_conf_bad():
    rhsm_parser = RHSMConf(context_wrap(RHSM_CONF_WITHOUT_HOSTNAME))
    broker = {RHSMConf: rhsm_parser}
    with pytest.raises(SkipComponent):
        base_url_of_satellite_api(broker)
    rhsm_parser = RHSMConf(context_wrap(RHSM_CONF_WITHOUT_PORT))
    broker = {RHSMConf: rhsm_parser}
    with pytest.raises(SkipComponent):
        base_url_of_satellite_api(broker)
