from insights.parsers import ParseException
from insights.parsers import pci_rport_target_disk_paths
from insights.parsers.pci_rport_target_disk_paths import PCIRportTargetDiskPaths as PCIPaths
from insights.tests import context_wrap
import pytest
import doctest


INPUT_GOOD = """/sys/devices/pci0000:00/0000:00:01.0/0000:04:00.6/host1/rport-1:0-1/target1:0:0/1:0:0:0/block/sdb
/sys/devices/pci0000:00/0000:00:01.0/0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0/block/sdc
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/ro
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/bdi
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/dev
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/sda1
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/sda2
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/size
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/stat
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/power
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/range
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/queue
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/trace
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/discard_alignment
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/device
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/events
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/subsystem
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/ext_range
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/slaves
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/uevent
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/events_poll_msecs
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/alignment_offset
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/holders
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/inflight
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/removable
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/capability
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/events_async
""".strip()


def test_good():
    pi = PCIPaths(context_wrap(INPUT_GOOD))
    print(type(pi['data'][0]['pci_id']))
    assert pi['data'][0]['pci_id'] == '0000:04:00.6'
    assert pi['data'][0]['target'] == 'target1:0:0'
    assert pi['data'][0]['rport'] == 'rport-1:0-1'
    assert pi['data'][0]['devnode'] == 'sdb'
    assert pi.pci_id == ['0000:04:00.6', '0000:04:00.7']

#def test_status_documentation():
#    """
#    Here we test the examples in the documentation automatically using
#    doctest.  We set up an environment which is similar to what a rule
#    writer might see - a '/usr/bin/vdo status' command output that has
#    been passed in as a parameter to the rule declaration.
#    """
#    env = {'vdo': VDOStatus(context_wrap(INPUT_STATUS_FULL))}
#    failed, total = doctest.testmod(vdo_status, globs=env)
#    assert failed == 0
#
#
#def test_status_exp():
#    """
#    Here test the examples cause expections
#    """
#    with pytest.raises(ParseException) as sc1:
#        VDOStatus(context_wrap(INPUT_EXP))
#    assert "couldn't parse yaml" in str(sc1)
#
#
#def test_status_exp3():
#    """
#    Here test the examples cause expections
#    """
#    with pytest.raises(KeyError) as sc1:
#        vdo = VDOStatus(context_wrap(INPUT_STATUS_SIMPLE))
#        vdo.get_physical_blocks_of_vol('vdo3')
#    assert "No key(s) named" in str(sc1)
