from insights.parsers.limits_conf import LimitsConf
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

LIMITS_CONF_PATH = "/etc/security/limits.conf"

BAD_LIMITS_CONF = """

oracle
oracle soft
oracle soft nofile
root       soft    nproc     unlimitied
"""

FULL_OPTS_LIMITS_CONF = """
# ** Domain variations **
# 0: User domain
oracle      soft nofile 1024
# 1: Group domain
@dbadmins   soft nofile 1024
# 2: Wildcard domain
*           soft nofile 2048
# 3: :maxuid - exact match
:1001       soft nofile 3072
# 4: minuid: - from that number up
1000:       soft nofile 1536
# 5: minuid:maxuid - range
2000:2020   soft nofile 1600
# 6: @:maxgid - exact match
@:101       soft nofile 4096
# 7: @mingid: - from that number up
@100:       soft nofile 2560
# 8: @minuid:maxuid - range
@200:202    soft nofile 2800

# ** Type variations **
# 9: Hard type
oracle      hard nofile 8192
# 10: Both types
managers    -    nofile 10240
"""


def test_class_conf():
    # The tests handle only a single file at this point...
    ctx = context_wrap(LIMITS_CONF, path=LIMITS_CONF_PATH)
    data = LimitsConf(ctx)

    assert data.domains == \
        sorted(['oracle', 'root'])


def test_class_bad():
    # The tests handle only a single file at this point...
    ctx = context_wrap(BAD_LIMITS_CONF, path=LIMITS_CONF_PATH)
    data = LimitsConf(ctx)

    assert data.domains == []
    bad_lines = BAD_LIMITS_CONF.strip().splitlines()
    assert data.bad_lines == bad_lines


def test_class_complete():
    # The tests handle only a single file at this point...
    ctx = context_wrap(FULL_OPTS_LIMITS_CONF, path=LIMITS_CONF_PATH)
    data = LimitsConf(ctx)

    assert data.domains == \
        sorted(
            ['oracle', '@dbadmins', '*', ':1001', '1000:', '2000:2020',
            '@:101', '@100:', '@200:202', 'managers']
        )

    # Data check
    assert data.rules[0] == \
        {'domain': 'oracle', 'type': 'soft', 'item': 'nofile', 'value': 1024, 'file': LIMITS_CONF_PATH}

    # User domain match
    # oracle soft, wildcard, and oracle hard
    assert data.find_all(domain='oracle') == \
        [data.rules[x] for x in [0, 2, 9]]
    # Group domain match
    # dbadmins group and wildcard
    assert data.find_all(domain='@dbadmins') == \
        [data.rules[x] for x in [1, 2]]
    # UID domain match
    # wildcard, uid 1001 exact, and uid range 1000:
    assert data.find_all(domain=1001) == \
        [data.rules[x] for x in [2, 3, 4]]
    # UID min range domain match
    # wildcard and uid range 1000:
    assert data.find_all(domain=1002) == \
        [data.rules[x] for x in [2, 4]]
    # UID min:max range match
    # wildcard, uid range 1000:, and uid range 2000:2020
    assert data.find_all(domain=2001) == \
        [data.rules[x] for x in [2, 4, 5]]
    # GID domain match
    # wildcard, gid 101 exact, and gid range 100:
    assert data.find_all(domain='@101') == \
        [data.rules[x] for x in [2, 6, 7]]
    # GID min range domain match
    # wildcard and gid range 100:
    assert data.find_all(domain='@102') == \
        [data.rules[x] for x in [2, 7]]
    # GID min:max range match
    # wildcard, gid range 100:, and gid range 200:202
    assert data.find_all(domain='@201') == \
        [data.rules[x] for x in [2, 7, 8]]
    # soft type match
    # most rules but not the hard rule
    assert data.find_all(type='soft') == \
        [data.rules[x] for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]]
    # hard type match
    # hard and both
    assert data.find_all(type='hard') == \
        [data.rules[x] for x in [9, 10]]
    # No match at all
    assert data.find_all(domain='postgres', type='hard') == \
        []
    # No rules to match
    assert data.find_all() == \
        []
