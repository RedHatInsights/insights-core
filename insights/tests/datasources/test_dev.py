import pytest

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.dev import physical_devices
from insights.combiners.virt_what import VirtWhat
from insights.core import dr
from insights.parsers.blkid import BlockIDInfo
from insights.parsers.virt_what import VirtWhat as VWP
from insights.tests import context_wrap


BLKID_INFO = """
/dev/sda1: UUID="3676157d-f2f5-465c-a4c3-fffffffff" TYPE="xfs"
/dev/sda2: UUID="UVTk76-UWOc-vk7s-galL-dxIP-fffffffff" TYPE="LVM2_member"
/dev/mapper/rhel_hp--dl160g8--3-root: UUID="11124c1d-990b-4277-9f74-fffffffff" TYPE="xfs"
/dev/mapper/rhel_hp--dl160g8--3-swap: UUID="c7c45f2d-1d1b-4cf0-9d51-fffffffff" TYPE="swap"
/dev/loop0: LABEL="Satellite-5.6.0 x86_64 Disc 0" TYPE="iso9660"
/dev/block/253:1: UUID="f8508c37-eeb1-4598-b084-fffffffff" TYPE="ext2"
/dev/sdb1: UUID="4676157d-f2f5-465c-a4c3-fffffffff" TYPE="xfs"
""".strip()

BLKID_INFO2 = """
/dev/vda1: UUID="3676157d-f2f5-465c-a4c3-fffffffff" TYPE="xfs"
/dev/vda2: UUID="UVTk76-UWOc-vk7s-galL-dxIP-fffffffff" TYPE="LVM2_member"
/dev/mapper/rhel_hp--dl160g8--3-root: UUID="11124c1d-990b-4277-9f74-fffffffff" TYPE="xfs"
/dev/mapper/rhel_hp--dl160g8--3-swap: UUID="c7c45f2d-1d1b-4cf0-9d51-fffffffff" TYPE="swap"
/dev/loop0: LABEL="Satellite-5.6.0 x86_64 Disc 0" TYPE="iso9660"
/dev/block/253:1: UUID="f8508c37-eeb1-4598-b084-fffffffff" TYPE="ext2"
/dev/vdb1: UUID="4676157d-f2f5-465c-a4c3-fffffffff" TYPE="xfs"
""".strip()

VW_OUT1 = """
kvm
""".strip()

# baremetal retuns blank
VW_OUT2 = """

""".strip()


def test_physical_devices():
    virt_what_info = VirtWhat(None, VWP(context_wrap(VW_OUT2)))
    blkid_info = BlockIDInfo(context_wrap(BLKID_INFO))

    broker = dr.Broker()
    broker[BlockIDInfo] = blkid_info
    broker[VirtWhat] = virt_what_info
    result = physical_devices(broker)
    assert result == ["/dev/sda", "/dev/sdb"]


def test_physical_devices_virt_env():
    virt_what_info = VirtWhat(None, VWP(context_wrap(VW_OUT1)))
    blkid_info = BlockIDInfo(context_wrap(BLKID_INFO))

    broker = dr.Broker()
    broker[BlockIDInfo] = blkid_info
    broker[VirtWhat] = virt_what_info
    with pytest.raises(SkipComponent):
        physical_devices(broker)


def test_physical_devices_virt_env2():
    virt_what_info = VirtWhat(None, VWP(context_wrap(VW_OUT1)))
    blkid_info = BlockIDInfo(context_wrap(BLKID_INFO2))

    broker = dr.Broker()
    broker[BlockIDInfo] = blkid_info
    broker[VirtWhat] = virt_what_info
    with pytest.raises(SkipComponent):
        physical_devices(broker)
