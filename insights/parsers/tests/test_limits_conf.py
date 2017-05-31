from insights.parsers import limits_conf
from insights.tests import context_wrap
import unittest

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


BAD_LIMITS_CONF = """

oracle
oracle soft
oracle soft nofile
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


class test_class(unittest.TestCase):
    def test_class_conf(self):
        # The tests handle only a single file at this point...
        ctx = context_wrap(LIMITS_CONF, path=LIMITS_CONF_PATH)
        data = limits_conf.LimitsConf(ctx)

        self.assertEqual(
            data.domains,
            sorted(['oracle', 'root'])
        )

    def test_class_bad(self):
        # The tests handle only a single file at this point...
        ctx = context_wrap(BAD_LIMITS_CONF, path=LIMITS_CONF_PATH)
        data = limits_conf.LimitsConf(ctx)

        self.assertEqual(data.domains, [])

    def test_class_complete(self):
        # The tests handle only a single file at this point...
        ctx = context_wrap(FULL_OPTS_LIMITS_CONF, path=LIMITS_CONF_PATH)
        data = limits_conf.LimitsConf(ctx)

        self.assertEqual(
            data.domains,
            sorted(
                ['oracle', '@dbadmins', '*', ':1001', '1000:', '2000:2020',
                '@:101', '@100:', '@200:202', 'managers']
            )
        )

        # Data check
        self.assertEqual(
            data.rules[0],
            {'domain': 'oracle', 'type': 'soft', 'item': 'nofile', 'value': 1024, 'file': LIMITS_CONF_PATH}
        )

        # User domain match
        self.assertEqual(
            data.find_all(domain='oracle'),
            # oracle soft, wildcard, and oracle hard
            [data.rules[x] for x in [0, 2, 9]]
        )
        # Group domain match
        self.assertEqual(
            data.find_all(domain='@dbadmins'),
            # dbadmins group and wildcard
            [data.rules[x] for x in [1, 2]]
        )
        # UID domain match
        self.assertEqual(
            data.find_all(domain=1001),
            # wildcard, uid 1001 exact, and uid range 1000:
            [data.rules[x] for x in [2, 3, 4]]
        )
        # UID min range domain match
        self.assertEqual(
            data.find_all(domain=1002),
            # wildcard and uid range 1000:
            [data.rules[x] for x in [2, 4]]
        )
        # UID min:max range match
        self.assertEqual(
            data.find_all(domain=2001),
            # wildcard, uid range 1000:, and uid range 2000:2020
            [data.rules[x] for x in [2, 4, 5]]
        )
        # GID domain match
        self.assertEqual(
            data.find_all(domain='@101'),
            # wildcard, gid 101 exact, and gid range 100:
            [data.rules[x] for x in [2, 6, 7]]
        )
        # GID min range domain match
        self.assertEqual(
            data.find_all(domain='@102'),
            # wildcard and gid range 100:
            [data.rules[x] for x in [2, 7]]
        )
        # GID min:max range match
        self.assertEqual(
            data.find_all(domain='@201'),
            # wildcard, gid range 100:, and gid range 200:202
            [data.rules[x] for x in [2, 7, 8]]
        )
        # soft type match
        self.assertEqual(
            data.find_all(type='soft'),
            # most rules but not the hard rule
            [data.rules[x] for x in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]]
        )
        # hard type match
        self.assertEqual(
            data.find_all(type='hard'),
            # hard and both
            [data.rules[x] for x in [9, 10]]
        )
        # No match at all
        self.assertEqual(
            data.find_all(domain='postgres', type='hard'),
            []
        )
        # No rules to match
        self.assertEqual(
            data.find_all(),
            []
        )
