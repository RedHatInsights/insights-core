import doctest
import pytest
from insights.parsers import sys_vmbus, SkipException
from insights.tests import context_wrap


BLANK = """
""".strip()

NO_RESULT = """
 Id    Name                           State
----------------------------------------------------
""".strip()

DEVICE_ID_1 = """
{47505500-0001-0000-3130-444531444234}
""".strip()

CLASS_ID_1 = """
{44c4f61d-4444-4400-9d52-802e27ede19f}
""".strip()

CLASS_ID_2 = """
{3375baf4-9e15-4b30-b765-67acb10d607b}
""".strip()

CLASS_ID_3 = """
{da0a7802-e377-4aac-8e77-0558eb1073f8}
""".strip()


def test_device_id():
    output = sys_vmbus.SysVmbusDeviceID(context_wrap(DEVICE_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/device_id'))
    assert output.file_name == 'device_id'
    assert output.id == '47505500-0001-0000-3130-444531444234'


def test_class_id():
    output = sys_vmbus.SysVmbusClassID(context_wrap(CLASS_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/class_id'))
    assert output.file_name == 'class_id'
    assert output.id == '44c4f61d-4444-4400-9d52-802e27ede19f'
    assert output.desc == 'PCI Express pass-through'

    output = sys_vmbus.SysVmbusClassID(context_wrap(CLASS_ID_2, path='/sys/bus/vmbus/devices/4487b255-b88c-403f-bb51-d1f69cf17f87/class_id'))
    assert output.file_name == 'class_id'
    assert output.id == '3375baf4-9e15-4b30-b765-67acb10d607b'
    assert output.desc == 'Unknown'

    output = sys_vmbus.SysVmbusClassID(context_wrap(CLASS_ID_3, path='/sys/bus/vmbus/devices/5620e0c7-8062-4dce-aeb7-520c7ef76171/class_id'))
    assert output.file_name == 'class_id'
    assert output.id == 'da0a7802-e377-4aac-8e77-0558eb1073f8'
    assert output.desc == 'Synthetic framebuffer adapter'


def test_blank_output():
    with pytest.raises(SkipException):
        output = sys_vmbus.SysVmbusDeviceID(context_wrap(BLANK, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/device_id'))
        assert output is None

    with pytest.raises(SkipException):
        output = sys_vmbus.SysVmbusClassID(context_wrap(BLANK, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/class_id'))
        assert output is None


def test_documentation():
    failed_count, tests = doctest.testmod(
        sys_vmbus,
        globs={
            'vmbus_device': sys_vmbus.SysVmbusDeviceID(context_wrap(DEVICE_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/device_id')),
            'vmbus_class': sys_vmbus.SysVmbusClassID(context_wrap(CLASS_ID_1, path='/sys/bus/vmbus/devices/47505500-0001-0000-3130-444531444234/class_id'))
        }
    )
    assert failed_count == 0
