from insights.parsers.sysconfig import KdumpSysconfig
from insights.tests import context_wrap

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
    sc_kdump = KdumpSysconfig(context_wrap(SYSCONFIG_KDUMP_ALL))
    assert sc_kdump is not None
    assert sc_kdump.KDUMP_KERNELVER == ""
    assert sc_kdump.KDUMP_COMMANDLINE == ""
    assert sc_kdump.KDUMP_COMMANDLINE_REMOVE == "hugepages hugepagesz slub_debug quiet"
    assert sc_kdump.KDUMP_COMMANDLINE_APPEND == "irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never"
    assert sc_kdump.KEXEC_ARGS == "--elf32-core-headers"
    assert sc_kdump.KDUMP_IMG == "vmlinuz"
    assert sc_kdump.KDUMP_IMG_EXT == ""
    assert sc_kdump.get("KDUMP_IMG") == "vmlinuz"

    sc_kdump = KdumpSysconfig(context_wrap(SYSCONFIG_KDUMP_SOME))
    assert sc_kdump is not None
    assert sc_kdump.KDUMP_KERNELVER == ""
    assert sc_kdump.KDUMP_COMMANDLINE == ""
    assert sc_kdump.KDUMP_COMMANDLINE_REMOVE == ""
    assert sc_kdump.KDUMP_COMMANDLINE_APPEND == "irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never"
    assert sc_kdump.KEXEC_ARGS == ""
    assert sc_kdump.KDUMP_IMG == "vmlinuz"
    assert sc_kdump.KDUMP_IMG_EXT == ""
    assert sc_kdump.get("KDUMP_IMG") == "vmlinuz"
