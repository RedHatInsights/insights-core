from falafel.mappers.vdsm_conf import VDSMConf
from falafel.tests import context_wrap


CONF = """

    [vars]
    ssl = true
    cpu_affinity = 1

    [addresses]
    management_port = 54321
    qq = 345
""".strip()


def test_vdsm_conf():
    result = VDSMConf(context_wrap(CONF))
    expected = {'vars': {'ssl': 'true', 'cpu_affinity': '1'}, 'addresses': {'management_port': '54321', 'qq': '345'}}
    assert result.data == expected
