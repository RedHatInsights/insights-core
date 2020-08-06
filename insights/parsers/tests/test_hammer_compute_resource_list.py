import doctest

from insights.parsers import hammer_compute_resource_list
from insights.parsers.hammer_compute_resource_list import HammerComputeResourceList
from insights.tests import context_wrap

CR_LIST_1 = """
[{"Id": 1, "Name": "kvm-server", "Provider": "Libvirt"}, {"Id": 4, "Name": "vCenter-1", "Provider": "VMware"}, {"Id": 3, "Name": "vCenter-2", "Provider": "VMware"}]
""".strip()

CR_LIST_2 = """[]"""


def test_hammer_compute_resource_list():
    cr_list = HammerComputeResourceList(context_wrap(CR_LIST_1))
    compute_resources = cr_list.data
    assert isinstance(compute_resources, list)
    assert len(compute_resources) == 3
    assert compute_resources[0] == {
        'Id': 1,
        'Name': 'kvm-server',
        'Provider': 'Libvirt',
    }
    assert set(cr_list.providers) == {'Libvirt', 'VMware'}

    cr_list = HammerComputeResourceList(context_wrap(CR_LIST_2))
    compute_resources = cr_list.data
    assert isinstance(compute_resources, list)
    assert len(compute_resources) == 0


def test_hammer_compute_resource_list_examples():
    env = {'compute_resource_list': HammerComputeResourceList(context_wrap(CR_LIST_1))}
    failed, total = doctest.testmod(hammer_compute_resource_list, globs=env)
    assert failed == 0
