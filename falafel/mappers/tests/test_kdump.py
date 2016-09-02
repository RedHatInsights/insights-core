import unittest

from falafel.mappers import kdump
from falafel.tests import context_wrap

CRASHKERNEL_MISS = """
ro root=/dev/VolGroup00/LogVol00 rhgb quiet
""".strip()

CRASHKERNEL_MATCH = """
ro root=/dev/VolGroup00/root rhgb quiet crashkernel=128M@16M single
""".strip()

KDUMP_DISABLED_RHEL6 = "kdump             0:off   1:off   2:off   3:off   4:off   5:off   6:off"
KDUMP_ENABLED_RHEL6 = "kdump             0:off   1:off   2:on    3:on    4:on    5:on    6:off"
KDUMP_DISABLED_RHEL7 = "kdump.service                               disabled"
KDUMP_ENABLED_RHEL7 = "kdump.service                               enabled"

KDUMP_MISS_1 = """
ssh kdumpuser@10.209.136.62
path /kdump/raw
core_collector makedumpfile -c --message-level 1 -d 31
""".strip()

KDUMP_MISS_2 = """
ext4 LABEL=nfs4
nfs4 my.server.com:/export/tmp
""".strip()

KDUMP_MATCH_1 = """
net user@raw.server.com
raw /dev/sda5
""".strip()

KDUMP_MATCH_2 = """
#ssh kdumpuser@10.209.136.62
#path /kdump/raw
#core_collector makedumpfile -c --message-level 1 -d 31
""".strip()

KDUMP_WITH_NORMAL_COMMENTS = """
# this is a comment

ssh kdumpuser@10.209.136.62
path /kdump/raw
core_collector makedumpfile -c --message-level 1 -d 31
""".strip()

KDUMP_WITH_INLINE_COMMENTS = """
ssh kdumpuser@10.209.136.62
path /kdump/raw #some path stuff
core_collector makedumpfile -c --message-level 1 -d 31
""".strip()

KDUMP_WITH_EQUAL = """
ssh kdumpuser@10.209.136.62
path /kdump/raw #some path stuff
core_collector makedumpfile -c --message-level 1 -d 31
some_var "blah=3"
""".strip()

KDUMP_WITH_EQUAL_2 = """
ssh kdumpuser@10.209.136.62
path /kdump/raw #some path stuff
core_collector makedumpfile -c --message-level 1 -d 31
KDUMP_COMMANDLINE_APPEND="blah"
""".strip()


class TestKDumpConf(unittest.TestCase):
    def test_with_normal_comments(self):
        context = context_wrap(KDUMP_WITH_NORMAL_COMMENTS)
        kd = kdump.KDumpConf.parse_context(context)
        expected = "# this is a comment"
        self.assertEqual(expected, kd.comments[0])

    def test_with_inline_comments(self):
        context = context_wrap(KDUMP_WITH_INLINE_COMMENTS)
        kd = kdump.KDumpConf.parse_context(context)
        expected = "path /kdump/raw #some path stuff"
        self.assertEqual(expected, kd.inline_comments[0])
        self.assertEqual("/kdump/raw", kd["path"])

    def test_with_equal(self):
        context = context_wrap(KDUMP_WITH_EQUAL)
        kd = kdump.KDumpConf.parse_context(context)
        expected = '"blah=3"'
        self.assertEqual(expected, kd['some_var'])

    def test_with_equal2(self):
        context = context_wrap(KDUMP_WITH_EQUAL_2)
        kd = kdump.KDumpConf.parse_context(context)
        expected = '"blah"'
        self.assertEqual(expected, kd['KDUMP_COMMANDLINE_APPEND'])

    def test_get_hostname(self):
        context = context_wrap(KDUMP_WITH_EQUAL)
        kd = kdump.KDumpConf.parse_context(context)
        self.assertEquals('10.209.136.62', kd.hostname)

        context = context_wrap(KDUMP_MATCH_1)
        kd = kdump.KDumpConf.parse_context(context)
        self.assertEquals('raw.server.com', kd.hostname)

    def test_get_ip(self):
        context = context_wrap(KDUMP_WITH_EQUAL)
        kd = kdump.KDumpConf.parse_context(context)
        self.assertEquals('10.209.136.62', kd.ip)

        context = context_wrap(KDUMP_MATCH_1)
        kd = kdump.KDumpConf.parse_context(context)
        self.assertTrue(kd.ip is None)


class TestKdump(unittest.TestCase):
    def test_crashkernel_enabled(self):
        self.assertEquals(None, kdump.crashkernel_enabled(context_wrap(CRASHKERNEL_MISS)))
        self.assertTrue(kdump.crashkernel_enabled(context_wrap(CRASHKERNEL_MATCH)))

    def test_kdump_service_enabled(self):
        self.assertTrue(kdump.kdump_service_enabled(context_wrap(KDUMP_ENABLED_RHEL6)))
        self.assertTrue(kdump.kdump_service_enabled(context_wrap(KDUMP_ENABLED_RHEL7)))
        self.assertEqual(None, kdump.kdump_service_enabled(context_wrap(KDUMP_DISABLED_RHEL6)))
        self.assertEqual(None, kdump.kdump_service_enabled(context_wrap(KDUMP_DISABLED_RHEL7)))

    def test_kdump_using_local_disk(self):
        r = kdump.kdump_using_local_disk(context_wrap(KDUMP_MISS_1))
        self.assertTrue(r is False or r is None)
        r = kdump.kdump_using_local_disk(context_wrap(KDUMP_MISS_2))
        self.assertTrue(r is False or r is None)
        self.assertTrue(kdump.kdump_using_local_disk(context_wrap(KDUMP_MATCH_1)))
        self.assertTrue(kdump.kdump_using_local_disk(context_wrap(KDUMP_MATCH_2)))
