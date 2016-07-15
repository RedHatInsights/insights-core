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
