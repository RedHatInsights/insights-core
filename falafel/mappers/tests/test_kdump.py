import unittest
from falafel.mappers import kdump
from falafel.tests import context_wrap

KDUMP_WITH_NORMAL_COMMENTS = """
# this is a comment

ssh kdumpuser@10.209.136.62
path /kdump/raw
core_collector makedumpfile -c --message-level 1 -d 31
""".strip()

KDUMP_WITH_INLINE_COMMENTS = """
nfs4 10.209.136.62:/kdumps
path /kdump/raw #some path stuff
core_collector makedumpfile -c --message-level 1 -d 31
""".strip()

KDUMP_WITH_EQUAL = """
nfs 10.209.136.62:/kdumps
path /kdump/raw #some path stuff
core_collector makedumpfile -c --message-level 1 -d 31
some_var "blah=3"
options bonding mode=active-backup miimon=100
""".strip()

KDUMP_WITH_BLACKLIST = """
path /var/crash
core_collector makedumpfile -c --message-level 1 -d 24
default shell
blacklist vxfs
blacklist vxportal
blacklist vxted
blacklist vxcafs
blacklist fdd
ignore_me
"""

KDUMP_WITH_NET = """
net user@raw.server.com
raw /dev/sda5
""".strip()

KDUMP_MATCH_1 = """
net user@raw.server.com
raw /dev/sda5
""".strip()


class TestKDumpConf(unittest.TestCase):
    def test_with_normal_comments(self):
        context = context_wrap(KDUMP_WITH_NORMAL_COMMENTS)
        kd = kdump.KDumpConf(context)
        expected = "# this is a comment"
        self.assertEqual(expected, kd.comments[0])
        # Also test is_* properties
        self.assertFalse(kd.is_nfs())
        self.assertTrue(kd.is_ssh())
        # Not a local disk then.
        self.assertFalse(kd.using_local_disk)

    def test_with_inline_comments(self):
        context = context_wrap(KDUMP_WITH_INLINE_COMMENTS)
        kd = kdump.KDumpConf(context)
        expected = "path /kdump/raw #some path stuff"
        self.assertEqual(expected, kd.inline_comments[0])
        self.assertEqual("/kdump/raw", kd["path"])
        # Also test is_* properties
        self.assertTrue(kd.is_nfs())
        self.assertFalse(kd.is_ssh())
        # Not a local disk then.
        self.assertFalse(kd.using_local_disk)

    def test_with_equal(self):
        context = context_wrap(KDUMP_WITH_EQUAL)
        kd = kdump.KDumpConf(context)
        expected = '"blah=3"'
        self.assertEqual(expected, kd['some_var'])
        self.assertIn('options', kd.data)
        self.assertIsInstance(kd.data['options'], dict)
        self.assertIn('bonding', kd.data['options'])
        self.assertEqual(
            'mode=active-backup miimon=100',
            kd.data['options']['bonding']
        )
        # Alternate accessor for options:
        self.assertEqual(kd.options('bonding'), 'mode=active-backup miimon=100')
        # Also test is_* properties
        self.assertTrue(kd.is_nfs())
        self.assertFalse(kd.is_ssh())
        # Not a local disk then.
        self.assertFalse(kd.using_local_disk)

    def test_get_hostname(self):
        context = context_wrap(KDUMP_WITH_EQUAL)
        kd = kdump.KDumpConf(context)
        self.assertEquals('10.209.136.62', kd.hostname)

        context = context_wrap(KDUMP_MATCH_1)
        kd = kdump.KDumpConf(context)
        self.assertEquals('raw.server.com', kd.hostname)

    def test_get_ip(self):
        context = context_wrap(KDUMP_WITH_EQUAL)
        kd = kdump.KDumpConf(context)
        self.assertEquals('10.209.136.62', kd.ip)

        context = context_wrap(KDUMP_MATCH_1)
        kd = kdump.KDumpConf(context)
        self.assertIsNone(kd.ip)

    def test_blacklist_repeated(self):
        context = context_wrap(KDUMP_WITH_BLACKLIST)
        kd = kdump.KDumpConf(context)
        self.assertIn('blacklist', kd.data)
        self.assertEqual(
            kd.data['blacklist'],
            ['vxfs', 'vxportal', 'vxted', 'vxcafs', 'fdd']
        )
        # Also test is_* properties
        self.assertFalse(kd.is_nfs())
        self.assertFalse(kd.is_ssh())
        self.assertTrue(kd.using_local_disk)

    def test_net_and_raw(self):
        context = context_wrap(KDUMP_WITH_NET)
        kd = kdump.KDumpConf(context)
        self.assertIn('net', kd.data)
        self.assertIn('raw', kd.data)
        self.assertTrue(kd.using_local_disk)
        with self.assertRaises(TypeError):
            self.assertTrue(kd[3])


SYSCONFIG_KDUMP_ALL = """
# Comments
KDUMP_KERNELVER=""

KDUMP_COMMANDLINE=""
KDUMP_COMMANDLINE_REMOVE="hugepages hugepagesz slub_debug quiet"
KDUMP_COMMANDLINE_APPEND="irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never"
KEXEC_ARGS="--elf32-core-headers"
KDUMP_IMG="vmlinuz"
KDUMP_IMG_EXT=""
"""

SYSCONFIG_KDUMP_SOME = """
# Comments
# Comments with apostrophes won't fool the dequoting process
KDUMP_COMMANDLINE_APPEND="irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never"
KDUMP_IMG="vmlinuz"
"""


def test_sysconfig_kdump():
    sc_kdump = kdump.SysconfigKdump(context_wrap(SYSCONFIG_KDUMP_ALL))
    assert sc_kdump is not None
    assert sc_kdump.KDUMP_KERNELVER == ""
    assert sc_kdump.KDUMP_COMMANDLINE == ""
    assert sc_kdump.KDUMP_COMMANDLINE_REMOVE == "hugepages hugepagesz slub_debug quiet"
    assert sc_kdump.KDUMP_COMMANDLINE_APPEND == "irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never"
    assert sc_kdump.KEXEC_ARGS == "--elf32-core-headers"
    assert sc_kdump.KDUMP_IMG == "vmlinuz"
    assert sc_kdump.KDUMP_IMG_EXT == ""
    assert sc_kdump.data.get("KDUMP_IMG") == "vmlinuz"

    sc_kdump = kdump.SysconfigKdump(context_wrap(SYSCONFIG_KDUMP_SOME))
    assert sc_kdump is not None
    assert sc_kdump.KDUMP_KERNELVER == ""
    assert sc_kdump.KDUMP_COMMANDLINE == ""
    assert sc_kdump.KDUMP_COMMANDLINE_REMOVE == ""
    assert sc_kdump.KDUMP_COMMANDLINE_APPEND == "irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never"
    assert sc_kdump.KEXEC_ARGS == ""
    assert sc_kdump.KDUMP_IMG == "vmlinuz"
    assert sc_kdump.KDUMP_IMG_EXT == ""
    assert sc_kdump.data.get("KDUMP_IMG") == "vmlinuz"


KEXEC_CRASH_SIZE_1 = "134217728"
KEXEC_CRASH_SIZE_2 = "0"
KEXEC_CRASH_SIZE_BAD = ""


def test_kexec_crash_size():
    kcs = kdump.KexecCrashSize(context_wrap(KEXEC_CRASH_SIZE_1))
    assert kcs.size == 134217728
    kcs = kdump.KexecCrashSize(context_wrap(KEXEC_CRASH_SIZE_2))
    assert kcs.size == 0
    kcs = kdump.KexecCrashSize(context_wrap(KEXEC_CRASH_SIZE_BAD))
    assert kcs.size == 0


KDUMP_CRASH_NOT_LOADED = '0'
KDUMP_CRASH_LOADED = '1'
KDUMP_CRASH_LOADED_BAD = ''


class TestKexecCrashLoaded(unittest.TestCase):
    def test_loaded(self):
        ctx = context_wrap(KDUMP_CRASH_LOADED, path='/sys/kernel/kexec_crash_loaded')
        self.assertTrue(kdump.KexecCrashLoaded(ctx).is_loaded)

    def test_not_loaded(self):
        ctx = context_wrap(KDUMP_CRASH_NOT_LOADED, path='/sys/kernel/kexec_crash_loaded')
        self.assertFalse(kdump.KexecCrashLoaded(ctx).is_loaded)

    def test_loaded_bad(self):
        ctx = context_wrap(KDUMP_CRASH_LOADED_BAD, path='/sys/kernel/kexec_crash_loaded')
        self.assertFalse(kdump.KexecCrashLoaded(ctx).is_loaded)
