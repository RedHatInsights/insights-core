import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import pci_rport_target_disk_paths
from insights.parsers.pci_rport_target_disk_paths import PciRportTargetDiskPaths as PCIPaths
from insights.tests import context_wrap


INPUT_GOOD = """/sys/devices/pci0000:00/0000:00:01.0/0000:04:00.6/host1/rport-1:0-1/target1:0:0/1:0:0:0/block/sdb/stat
/sys/devices/pci0000:00/0000:00:01.0/0000:04:00.7/host2/rport-2:0-2/target2:0:0/2:0:0:0/block/sdc/stat
/sys/devices/pci0000:00/0000:00:02.2/0000:02:00.0/host0/target0:1:0/0:1:0:0/block/sda/stat
""".strip()


INPUT_BAD = """
/sys/devices/pci0000:00/block/sda/stat
/sys/devices/pci0000:00/block/sda/device
/sys/devices/pci0000:00/block/sda/events
/sys/devices/pci0000:00/block/sda/subsystem
/sys/devices/pci0000:00/block/sda/ext_range
/sys/devices/pci0000:00/block/sda/slaves
/sys/devices/pci0000:00/block/sda/uevent
/sys/devices/pci0000:00/block/sda/events_poll_msecs
/sys/devices/pci0000:00/block/sda/alignment_offset
/sys/devices/pci0000:00/block/sda/holders
/sys/devices/pci0000:00/block/sda/inflight
/sys/devices/pci0000:00/block/sda/removable
/sys/devices/pci0000:00/block/sda/capability
/sys/devices/pci0000:00/block/sda/events_async
""".strip()


def test_good():
    pi = PCIPaths(context_wrap(INPUT_GOOD))
    assert pi.path_list[0]['pci_id'] == '0000:04:00.6'
    assert pi.path_list[0]['target'] == 'target1:0:0'

    assert pi.path_list[0]['rport'] == 'rport-1:0-1'
    assert pi.path_list[0]['devnode'] == 'sdb'

    assert pi.pci_id == ['0000:02:00.0', '0000:04:00.6', '0000:04:00.7']
    assert pi.devnode == ['sda', 'sdb', 'sdc']

    assert pi.host == ['host0', 'host1', 'host2']
    assert pi.target == ['target0:1:0', 'target1:0:0', 'target2:0:0']

    assert pi.rport == ['rport-1:0-1', 'rport-2:0-2']
    assert pi.host_channel_id_lun == ['0:1:0:0', '1:0:0:0', '2:0:0:0']


def test_status_documentation():
    """
    Here we test the examples in the documentation automatically using doctest
    . We set up an environment which is similar to what a rule writer might
    see - a '/usr/bin/find /sys/devices/pci0000:00 -mindepth 8 -maxdepth 8' command
    output that has been passed in as a parameter to the rule declaration.
    """
    env = {'pd': PCIPaths(context_wrap(INPUT_GOOD))}
    failed, total = doctest.testmod(pci_rport_target_disk_paths, globs=env)
    assert failed == 0


def test_status_exp():
    """
    Here test the examples cause expections
    """
    with pytest.raises(SkipComponent) as sc1:
        PCIPaths(context_wrap(''))
    assert "Input content is empty" in str(sc1)


def test_status_exp2():
    """
    Here test the examples cause expections
    """
    with pytest.raises(ParseException) as sc1:
        PCIPaths(context_wrap(INPUT_BAD))
    assert "No useful data parsed in line" in str(sc1)
