import doctest
import pytest

from insights.parsers import lsvmbus
from insights.parsers import SkipException
from insights.tests import context_wrap


OUTPUT = """
VMBUS ID 18: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
        Device_ID = {47505500-0001-0000-3130-444531303244}
        Sysfs path: /sys/bus/vmbus/devices/47505500-0001-0000-3130-444531303244
        Rel_ID=18, target_cpu=0
VMBUS ID 26: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
        Device_ID = {47505500-0002-0000-3130-444531303244}
        Sysfs path: /sys/bus/vmbus/devices/47505500-0002-0000-3130-444531303244
        Rel_ID=26, target_cpu=0
VMBUS ID 73: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
        Device_ID = {47505500-0003-0001-3130-444531303244}
        Sysfs path: /sys/bus/vmbus/devices/47505500-0003-0001-3130-444531303244
        Rel_ID=73, target_cpu=0
VMBUS ID 74: Class_ID = {44c4f61d-4444-4400-9d52-802e27ede19f} - PCI Express pass-through
        Device_ID = {47505500-0004-0001-3130-444531303244}
        Sysfs path: /sys/bus/vmbus/devices/47505500-0004-0001-3130-444531303244
        Rel_ID=74, target_cpu=0
""".strip()


def test_lsvmbus():
    output = lsvmbus.LsvmBus(context_wrap(OUTPUT))
    assert len(output.devices) == 4
    assert output.devices[0].get('vmbus_id', None) == '18'
    assert output.devices[0].get('device_id', None) == '47505500-0001-0000-3130-444531303244'
    assert output.devices[0].get('rel_id', None) == '18'
    assert output.devices[0].get('sysfs_path', None) == '/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531303244'
    assert output.devices[0].get('target_cpu', None) == '0'

    with pytest.raises(SkipException):
        assert lsvmbus.LsvmBus(context_wrap("")) is None


def test_docs():
    env = {'lsvmbus': lsvmbus.LsvmBus(context_wrap(OUTPUT))}
    failed, total = doctest.testmod(lsvmbus, globs=env)
    assert failed == 0
