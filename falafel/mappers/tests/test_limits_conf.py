from falafel.mappers import limits_conf
from falafel.tests import context_wrap

LIMITS_CONF = """
#oracle soft nproc 2047
#oracle hard nproc 16384
oracle soft nofile 1024
oracle hard nofile 65536
oracle soft stack 10240
oracle hard stack 3276
root       soft    nproc     unlimited
""".strip()

LIMITS_D_CONF = """
@jackuser - rtprio 70
@jackuser - memlock 4194304
""".strip()

LIMITS_CONF_PATH = "etc/security/limits.conf"
LIMITS_D_PATH = "etc/security/limits.d/95-jack.conf"


def test_limits_conf():
    data = limits_conf.get_limits(context_wrap(LIMITS_CONF, path=LIMITS_CONF_PATH))
    assert len(data.get('limits.conf')) == 5
    assert data.get('limits.conf') == [{'domain': 'oracle', 'type': 'soft', 'item': 'nofile', 'value': 1024},
                                       {'domain': 'oracle', 'type': 'hard', 'item': 'nofile', 'value': 65536},
                                       {'domain': 'oracle', 'type': 'soft', 'item': 'stack', 'value': 10240},
                                       {'domain': 'oracle', 'type': 'hard', 'item': 'stack', 'value': 3276},
                                       {'domain': 'root', 'type': 'soft', 'item': 'nproc', 'value': -1}]


def test_limits_d():
    data = limits_conf.get_limits(context_wrap(LIMITS_D_CONF, path=LIMITS_D_PATH))
    assert len(data.get('95-jack.conf')) == 2
    assert data.get('95-jack.conf') == [{'domain': '@jackuser', 'type': '-', 'item': 'rtprio', 'value': 70},
                                        {'domain': '@jackuser', 'type': '-', 'item': 'memlock', 'value': 4194304}]
