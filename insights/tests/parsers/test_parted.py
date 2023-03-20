import pytest
import doctest

from insights.core.exceptions import ParseException
from insights.parsers import parted
from insights.parsers.parted import PartedDevice, PartedL
from insights.tests import context_wrap

PARTED_DATA = """
Model: Virtio Block Device (virtblk)
Disk /dev/vda: 9664MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags:

Number  Start   End     Size    Type     File system  Flags
 1      1049kB  525MB   524MB   primary  xfs          boot
 2      525MB   9664MB  9138MB  primary               lvm
""".strip()

PARTED_DATA_NO_SECTOR_SPLIT = """
Model: Virtio Block Device (virtblk)
Disk /dev/vda: 9664MB
Sector size (logical/physical): 512B
Partition Table: msdos
Disk Flags:

Number  Start   End     Size    Type     File system  Flags
 1      1049kB  525MB   524MB   primary  xfs          boot
 2      525MB   9664MB  9138MB  primary               lvm
"""

PARTED_DATA_2 = """
Model: IBM 2107900 (scsi)
Disk /dev/sdet: 2147MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      32.3kB  2580kB  2548kB  primary
""".strip()

PARTED_DATA_3 = """
Model: DELL PERC H710 (scsi)
Disk /dev/sda: 292GB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type      File system  Flags
 1      32.3kB  526MB   526MB   primary   ext3         boot
 2      526MB   9114MB  8587MB  primary   linux-swap
 3      9114MB  12.3GB  3224MB  primary   ext3
 4      12.3GB  292GB   280GB   extended
 5      12.3GB  254GB   241GB   logical   ext3
 6      254GB   281GB   26.8GB  logical   ext3
 7      281GB   285GB   4294MB  logical   ext3
 8      285GB   288GB   3224MB  logical   ext3
 9      288GB   290GB   2147MB  logical   ext3
10      290GB   292GB   2147MB  logical   ext3
""".strip()

PARTED_DATA_4 = """
Model: DELL PERC H710 (scsi)
Disk /dev/sda: 2399GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: pmbr_boot

Number  Start   End     Size    File system  Name                  Flags
 1      1049kB  525MB   524MB   fat32        EFI system partition  boot
 2      525MB   567MB   41.9MB  fat32        Basic data partition  hidden
 3      567MB   2715MB  2147MB  fat32        Basic data partition
 4      2715MB  2716MB  1049kB                                     bios_grub
 5      2716MB  3240MB  524MB   xfs
 6      3240MB  2077GB  2074GB                                     lvm


Model: Linux device-mapper (linear) (dm)
Disk /dev/mapper/rhel_home: 191GB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End    Size   File system  Flags
 1      0.00B  191GB  191GB  xfs


Model: Linux device-mapper (linear) (dm)
Disk /dev/mapper/rhel_iso: 161GB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End    Size   File system  Flags
 1      0.00B  161GB  161GB  xfs


Model: Linux device-mapper (linear) (dm)
Disk /dev/mapper/rhel_vms: 1611GB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End     Size    File system  Flags
 1      0.00B  1611GB  1611GB  xfs


Model: Linux device-mapper (linear) (dm)
Disk /dev/mapper/rhel_lvtest: 4194kB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End     Size    File system  Flags
 1      0.00B  4194kB  4194kB  ext4


Model: Linux device-mapper (linear) (dm)
Disk /dev/mapper/rhel_root: 107GB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End    Size   File system  Flags
 1      0.00B  107GB  107GB  xfs


Model: Linux device-mapper (linear) (dm)
Disk /dev/mapper/rhel_swap: 4295MB
Sector size (logical/physical): 512B/512B
Partition Table: loop
Disk Flags:

Number  Start  End     Size    File system     Flags
 1      0.00B  4295MB  4295MB  linux-swap(v1)
""".strip()

PARTED_DATA_5 = """
Model: VMware Virtual disk (scsi)
Disk /dev/sda: 94371840s
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start     End        Size       File system  Name                  Flags
 1      2048s     2099199s   2097152s   fat32        EFI System Partition  boot, esp
 2      2099200s  4196351s   2097152s   xfs
 3      4196352s  83904511s  79708160s                                     lvm


Error: /dev/sdb: unrecognised disk label
Model: VMware Virtual disk (scsi)
Disk /dev/sdb: 75497472s
Sector size (logical/physical): 512B/512B
Partition Table: unknown
Disk Flags:


Model: VMware Virtual disk (scsi)
Disk /dev/sdc: 15032385536s
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags:

Number  Start  End          Size         Type     File system  Flags
 1      2048s  4294967294s  4294965247s  primary  xfs


Model: VMware Virtual disk (scsi)
Disk /dev/sdd: 629145600s
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags:

Number  Start  End         Size        Type     File system  Flags
 1      2048s  629145599s  629143552s  primary  xfs


Error: /dev/sde: unrecognised disk label
Model: VMware Virtual disk (scsi)
Disk /dev/sde: 2097152s
Sector size (logical/physical): 512B/512B
Partition Table: unknown
Disk Flags:
""".strip()

PARTED_DATA_6 = """
Model: VMware Virtual disk (scsi)
Disk /dev/sda: 94371840s
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags:

Number  Start     End        Size       File system  Name                  Flags
 1      2048s     2099199s   2097152s   fat32        EFI System Partition  boot, esp
 2      2099200s  4196351s   2097152s   xfs
 3      4196352s  83904511s  79708160s                                     lvm
""".strip()


def test_parted_partedl():
    context = context_wrap(PARTED_DATA)
    res = PartedL(context)
    results = res.devices_info[0]
    assert results is not None
    assert results.get('model') == 'Virtio Block Device (virtblk)'
    assert results.disk == '/dev/vda'
    assert results.get('size') == '9664MB'
    assert results.get('sector_size') == '512B/512B'
    assert results.logical_sector_size == '512B'
    assert results.physical_sector_size == '512B'
    assert results.get('partition_table') == 'msdos'
    assert results.get('disk_flags') is None
    partitions = results.partitions
    assert len(partitions) == 2
    assert partitions[0].number == '1'
    assert partitions[0].start == '1049kB'
    assert partitions[0].end == '525MB'
    assert partitions[0].size == '524MB'
    assert partitions[0].file_system == 'xfs'
    assert partitions[0].get('name') is None
    assert partitions[0].type == 'primary'
    assert partitions[0].flags == 'boot'
    assert results.boot_partition is not None
    assert results.boot_partition.number == '1'

    assert partitions[1].get('file_system') == ''
    assert partitions[1].get('flags') == 'lvm'
    assert partitions[1].get('name') is None
    assert partitions[1].get('number') == '2'
    assert partitions[1].get('start') == '525MB'
    assert partitions[1].get('end') == '9664MB'
    assert partitions[1].get('size') == '9138MB'
    assert partitions[1].get('type') == 'primary'

    context = context_wrap(PARTED_DATA_2)
    res = PartedL(context)
    results = res.devices_info[0]
    assert results is not None
    assert results.disk == '/dev/sdet'
    assert len(results.partitions) == 1

    context = context_wrap(PARTED_DATA_3)
    res = PartedL(context)
    results = res.devices_info[0]
    assert results is not None
    assert results.disk == '/dev/sda'
    assert results.logical_sector_size == '512B'
    assert results.physical_sector_size == '512B'
    assert len(results.partitions) == 10

    context = context_wrap(PARTED_DATA_4)
    res = PartedL(context)
    all_disks = [dev_info.disk for dev_info in res]
    assert all_disks == ['/dev/sda',
                         '/dev/mapper/rhel_home',
                         '/dev/mapper/rhel_iso',
                         '/dev/mapper/rhel_vms',
                         '/dev/mapper/rhel_lvtest',
                         '/dev/mapper/rhel_root',
                         '/dev/mapper/rhel_swap']

    dev_sda = res.get('/dev/sda')
    for dev_info in res:
        assert dev_info == dev_sda
        break

    dev_mapper_rhel_home = res.get('/dev/mapper/rhel_root')
    assert len(dev_mapper_rhel_home.partitions) == 1
    assert res.get('/dev/sdb') is None

    context = context_wrap(PARTED_DATA_5)
    res = PartedL(context)
    assert len([dev_info.disk for dev_info in res]) == 3

    results = res.get('/dev/sdc')
    assert results.get('size') == '15032385536s'
    assert results.get('model') == 'VMware Virtual disk (scsi)'
    assert results.get('sector_size') == '512B/512B'
    assert results.get('partition_table') == 'msdos'
    assert results.get('disk_flags') is None


PARTED_ERR_DATA = """
Error: /dev/dm-1: unrecognised disk label
"""

PARTED_ERR_DATA_2 = """
Model: IBM 2107900 (scsi)
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      32.3kB  2580kB  2548kB  primary
""".strip()

PARTED_ERR_DATA_NO_PARTITIONS = """
Model: Virtio Block Device (virtblk)
Disk /dev/vda: 9664MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos
Disk Flags:

"""

PARTED_ERR_DATA_EXCEPTIONS = """
Model: Virtio Block Device (virtblk)
Disk /dev/vda: 9664MB
Sector size (logical:physical): 512B:512B
Partition Table: msdos
Disk Flags:

Number  Start   End     Size    Type     File system  Flags
"""


def test_failure_modes():
    with pytest.raises(ParseException):
        PartedDevice(PARTED_ERR_DATA.split('\n'))

    context = context_wrap(PARTED_ERR_DATA)
    res = PartedL(context)
    assert len(res.devices_info) == 0

    with pytest.raises(ParseException):
        PartedDevice(PARTED_ERR_DATA_2.split('\n'))

    context = context_wrap(PARTED_ERR_DATA_2)
    res = PartedL(context)
    assert len(res.devices_info) == 0

    # Test failure to find a slash in sector size
    res = PartedL(context_wrap(PARTED_DATA_NO_SECTOR_SPLIT))
    results = res.devices_info[0]
    assert results is not None
    assert results.disk == '/dev/vda'
    assert results._sector_size is None
    assert results.logical_sector_size is None
    assert results.physical_sector_size is None

    # Object should be complete but has no data
    res = PartedL(context_wrap(PARTED_ERR_DATA_NO_PARTITIONS))
    part = res.devices_info[0]
    assert part is not None
    assert part.disk == '/dev/vda'
    assert part.data['sector_size'] == '512B/512B'
    assert part.logical_sector_size == '512B'
    assert part.physical_sector_size == '512B'
    assert part.partitions == []

    # Various other failure modes that aren't actual parse exceptions atm
    res = PartedL(context_wrap(PARTED_ERR_DATA_EXCEPTIONS))
    part = res.devices_info[0]
    assert part.disk == '/dev/vda'
    assert 'sector_size' not in part.data


PARTED_DOC_TEST_1 = """
Model: ATA TOSHIBA MG04ACA4 (scsi)
Disk /dev/sda: 4001GB
Sector size (logical/physical): 512B/512B
Partition Table: gpt
Disk Flags: pmbr_boot

Number  Start   End     Size    File system  Name  Flags
 1      1049kB  2097kB  1049kB                     bios_grub
 2      2097kB  526MB   524MB   xfs
 3      526MB   4001GB  4000GB                     lvm


Model: IBM 2107900 (scsi)
Disk /dev/sdb: 2147MB
Sector size (logical/physical): 512B/512B
Partition Table: msdos

Number  Start   End     Size    Type     File system  Flags
 1      32.3kB  2580kB  2548kB  primary
"""


def test_doc_examples():
    env = {
        'parted_l_results': PartedL(context_wrap(PARTED_DOC_TEST_1)),
    }
    failed, total = doctest.testmod(parted, globs=env)
    assert failed == 0
