import doctest
import pytest

from insights.tests import context_wrap
from insights.parsers import SkipException, system_devices

SYSTEM_DEVICES1 = """
# LVM uses devices listed in this file.
# Created by LVM command lvmdevices pid 2631 at Fri May 27 07:37:11 2022
VERSION=1.1.2
IDTYPE=devname IDNAME=/dev/vda2 DEVNAME=/dev/vda2 PVID=phl0clFbAokp9UXqbIgI5YYQxuTIJVkD PART=2
""".strip()

SYSTEM_DEVICES2 = """
# LVM uses devices listed in this file.
# Created by LVM command lvmdevices pid 2631 at Fri May 27 07:37:11 2022
VERSION=1.1.2
IDTYPE=sys_wwid IDNAME=/dev/vda2 DEVNAME=/dev/vda2 PVID=phl0clFbAokp9UXqbIgI5YYQxuTIJVkD PART=2
IDTYPE=sys_serial IDNAME=/dev/vda1 DEVNAME=/dev/vda1 PVID=phl0clFbAokp9UXqbIgI5YYQdeTIJVkD PART=1
""".strip()

SYSTEM_DEVICES3 = """
# LVM uses devices listed in this file.
# Created by LVM command lvmdevices pid 2631 at Fri May 27 07:37:11 2022
VERSION=1.1.2
""".strip()


def test_system_devices():
    devices = system_devices.SystemDevices(context_wrap(SYSTEM_DEVICES2))
    assert len(devices) == 2
    assert '/dev/vda1' in devices
    assert devices['/dev/vda1']['IDTYPE'] == 'sys_serial'
    assert '/dev/vda2' in devices
    assert devices['/dev/vda2']['IDTYPE'] == 'sys_wwid'


def test_system_devices_exception():
    with pytest.raises(SkipException):
        system_devices.SystemDevices(context_wrap(SYSTEM_DEVICES3))


def test_docs():
    env = {
        'devices': system_devices.SystemDevices(context_wrap(SYSTEM_DEVICES1))
    }
    failed, total = doctest.testmod(system_devices, globs=env)
    assert failed == 0
