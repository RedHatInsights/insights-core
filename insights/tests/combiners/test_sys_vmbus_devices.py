import doctest

from insights.combiners import sys_vmbus_devices
from insights.parsers.sys_vmbus import SysVmbusDeviceID, SysVmbusClassID
from insights.tests import context_wrap


DEVICE_ID_1 = """
{47505500-0001-0000-3130-444531444234}
""".strip()

CLASS_ID_1 = """
{44c4f61d-4444-4400-9d52-802e27ede19f}
""".strip()

DEVICE_ID_2 = """
{4487b255-b88c-403f-bb51-d1f69cf17f87}
""".strip()

CLASS_ID_2 = """
{3375baf4-9e15-4b30-b765-67acb10d607b}
""".strip()


def test_sys_vmbus_devices_combiner():
    result = sys_vmbus_devices.SysVmBusDeviceInfo(
        [
            SysVmbusDeviceID(context_wrap(DEVICE_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/device_id')),
            SysVmbusDeviceID(context_wrap(DEVICE_ID_2, path='/sys/bus/vmbus/devices/4487b255-b88c-403f-bb51-d1f69cf17f87/device_id')),
        ],
        [
            SysVmbusClassID(context_wrap(CLASS_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/class_id')),
            SysVmbusClassID(context_wrap(CLASS_ID_2, path='/sys/bus/vmbus/devices/4487b255-b88c-403f-bb51-d1f69cf17f87/class_id'))
        ]
    )

    assert result.devices[0].get('device_id') == '47505500-0001-0000-3130-444531444234'
    assert result.devices[0].get('class_id') == '44c4f61d-4444-4400-9d52-802e27ede19f'
    assert result.devices[0].get('description') == 'PCI Express pass-through'

    assert result.devices[-1].get('device_id') == '4487b255-b88c-403f-bb51-d1f69cf17f87'
    assert result.devices[-1].get('class_id') == '3375baf4-9e15-4b30-b765-67acb10d607b'
    assert result.devices[-1].get('description') == 'Unknown'


def test_documentation():
    result = sys_vmbus_devices.SysVmBusDeviceInfo(
        [
            SysVmbusDeviceID(context_wrap(DEVICE_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/device_id')),
            SysVmbusDeviceID(context_wrap(DEVICE_ID_2, path='/sys/bus/vmbus/devices/4487b255-b88c-403f-bb51-d1f69cf17f87/device_id')),
        ],
        [
            SysVmbusClassID(context_wrap(CLASS_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/class_id')),
            SysVmbusClassID(context_wrap(CLASS_ID_2, path='/sys/bus/vmbus/devices/4487b255-b88c-403f-bb51-d1f69cf17f87/class_id'))
        ]
    )

    failed_count, tests = doctest.testmod(
        sys_vmbus_devices,
        globs={
            'output': result
        }
    )
    assert failed_count == 0
