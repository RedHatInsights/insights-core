import doctest
import pytest

from insights.parsers import lsvmbus
from insights.parsers import SkipException
from insights.tests import context_wrap


OUTPUT = """
[{'device_id': '5620e0c7-8062-4dce-aeb7-520c7ef76171', 'class_id': 'da0a7802-e377-4aac-8e77-0558eb1073f8', 'description': 'Synthetic framebuffer adapter'}, {'device_id': '47505500-0001-0000-3130-444531444234', 'class_id': '44c4f61d-4444-4400-9d52-802e27ede19f', 'description': 'PCI Express pass-through'}, {'device_id': '4487b255-b88c-403f-bb51-d1f69cf17f87', 'class_id': '3375baf4-9e15-4b30-b765-67acb10d607b', 'description': 'Unknown'}]
""".strip()


def test_lsvmbus():
    output = lsvmbus.LsVMBus(context_wrap(OUTPUT))
    # import pdb; pdb.set_trace()
    assert len(output.devices) == 3
    assert output.devices[1].get('device_id', None) == '47505500-0001-0000-3130-444531444234'
    assert output.devices[1].get('description', None) == 'PCI Express pass-through'

    with pytest.raises(SkipException):
        assert lsvmbus.LsVMBus(context_wrap("")) is None


def test_docs():
    env = {'lsvmbus': lsvmbus.LsVMBus(context_wrap(OUTPUT))}
    failed, total = doctest.testmod(lsvmbus, globs=env)
    assert failed == 0
