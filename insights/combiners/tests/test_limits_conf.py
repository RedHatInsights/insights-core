from insights.parsers.limits_conf import LimitsConf
from insights.combiners.limits_conf import AllLimitsConf
from insights.tests import context_wrap

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

DUP_LIMITS_D_CONF = """
oracle hard stack 1926
"""

LIMITS_CONF_PATH = "/etc/security/limits.conf"
LIMITS_D_PATH = "/etc/security/limits.d/95-jack.conf"
DUP_LIMITS_D_CONF_PATH = "/etc/security/limits.d/oracle.conf"


def test_all_limits_conf():
    data1 = LimitsConf(context_wrap(LIMITS_CONF, path=LIMITS_CONF_PATH))
    data2 = LimitsConf(context_wrap(LIMITS_D_CONF, path=LIMITS_D_PATH))
    all_data = AllLimitsConf([data1, data2])

    assert len(all_data.rules) == 7
    assert all_data.rules[0] == {'domain': 'oracle', 'type': 'soft', 'item': 'nofile', 'value': 1024, 'file': LIMITS_CONF_PATH}
    assert all_data.rules[1] == {'domain': 'oracle', 'type': 'hard', 'item': 'nofile', 'value': 65536, 'file': LIMITS_CONF_PATH}
    assert all_data.rules[2] == {'domain': 'oracle', 'type': 'soft', 'item': 'stack', 'value': 10240, 'file': LIMITS_CONF_PATH}
    assert all_data.rules[3] == {'domain': 'oracle', 'type': 'hard', 'item': 'stack', 'value': 3276, 'file': LIMITS_CONF_PATH}
    assert all_data.rules[4] == {'domain': 'root', 'type': 'soft', 'item': 'nproc', 'value': -1, 'file': LIMITS_CONF_PATH}
    assert all_data.rules[5] == {'domain': '@jackuser', 'type': '-', 'item': 'rtprio', 'value': 70, 'file': LIMITS_D_PATH}
    assert all_data.rules[6] == {'domain': '@jackuser', 'type': '-', 'item': 'memlock', 'value': 4194304, 'file': LIMITS_D_PATH}

    assert all_data.domains == set(['oracle', 'root', '@jackuser'])

    assert all_data.find_all(domain='root') == [all_data.rules[4]]

    data3 = LimitsConf(context_wrap(DUP_LIMITS_D_CONF, path=DUP_LIMITS_D_CONF_PATH))
    all_data = AllLimitsConf([data1, data3])
    # Check de-duplication of rules
    assert len(all_data.rules) == 5  # No extra rule
    assert all_data.rules[3] == {'domain': 'oracle', 'type': 'hard', 'item': 'stack', 'value': 1926, 'file': DUP_LIMITS_D_CONF_PATH}
