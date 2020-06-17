from insights.parsers import hammer_compute_resource_list
from insights.tests import context_wrap
import pytest
from insights.parsers import SkipException

hammer_compute_resource_list_json_data = '''
[{"Id": 1, "Name": "kvm-server", "Provider": "Libvirt"}, {"Id": 4, "Name": "VMWARE", "Provider": "VMware"}, {"Id": 3, "Name": "vmware67", "Provider": "VMware"}]
'''


def test_hammer_compute_resource_list():
    hammer_compute_resource_list.HammerComputeResourceList(context_wrap(hammer_compute_resource_list_json_data))


def test_no_data():
    with pytest.raises(SkipException) as ex:
        hammer_compute_resource_list.HammerComputeResourceList(context_wrap(''))
    assert 'No content or hammer auth failed.' in str(ex)
