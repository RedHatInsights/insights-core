from insights.parsers import mdadm
from insights.parsers.mdadm import MDAdmMetadata, MDAdmDetail
from insights.core.exceptions import SkipComponent
from insights.tests import context_wrap

import doctest
import pytest

MDADM_CONTENT = """
/dev/loop0:
Magic : a92b4efc
Version : 1.0
Feature Map : 0x0
Array UUID : 98e098ef:c8662ce2:2ed2aa5f:7f0416a9
Name : 0
Creation Time : Mon Jun 29 02:16:52 2020
Raid Level : raid1
Raid Devices : 2

Avail Dev Size : 16383968 sectors (7.81 GiB 8.39 GB)
Array Size : 1048576 KiB (1024.00 MiB 1073.74 MB)
Used Dev Size : 2097152 sectors (1024.00 MiB 1073.74 MB)
Super Offset : 16383984 sectors
Unused Space : before=0 sectors, after=14286824 sectors
State : clean
Device UUID : 5e249ed9:a9ee800a:c09c963f:363a18d2

Update Time : Mon Jun 29 02:19:56 2020
Bad Block Log : 512 entries available at offset -8 sectors
Checksum : 395066e8 - correct
Events : 60

Device Role : Active device 0
Array State : AA ('A' == active, '.' == missing, 'R' == replacing)
"""  # noqa


def test_mdadm():
    md = MDAdmMetadata(context_wrap(
        MDADM_CONTENT, path='insights_commands/mdadm_-E_.dev.loop0'
    ))

    # Device assertions
    assert md.device == '/dev/loop0'

    # Information assertions
    assert md['Update Time'] == 'Mon Jun 29 02:19:56 2020'
    assert md['Array Size'] == '1048576 KiB (1024.00 MiB 1073.74 MB)'

    with pytest.raises(SkipComponent) as exc:
        MDAdmMetadata(context_wrap(MDADM_CONTENT))
    assert 'Cannot parse device name from path' in str(exc)


MDADM_D_CONTENT_MD0 = """
/dev/md0:
           Version : 1.2
     Creation Time : Wed Mar 24 14:28:18 2021
        Raid Level : raid5
        Array Size : 21877481472 (20.37 TiB 22.40 TB)
     Used Dev Size : 1562677248 (1490.29 GiB 1600.18 GB)
      Raid Devices : 21
     Total Devices : 22
       Persistence : Superblock is persistent

     Intent Bitmap : Internal

       Update Time : Sat May 13 07:21:53 2023
             State : active, reshaping
    Active Devices : 21
   Working Devices : 22
    Failed Devices : 0
     Spare Devices : 1

            Layout : left-symmetric
        Chunk Size : 512K

Consistency Policy : bitmap

    Reshape Status : 28% complete
     Delta Devices : 6, (15->21)

              Name : hostname:0  (local to host hostname)
              UUID : 245e1231:245e1231:245e1231:245e1231
            Events : 372252

    Number   Major   Minor   RaidDevice State
       0       8      225        0      active sync   /dev/sdo1
       1       8      241        1      active sync   /dev/sdp1
       2       8      177        2      active sync   /dev/sdl1
       3       8      209        3      active sync   /dev/sdn1
       4       8      161        4      active sync   /dev/sdk1
       5       8      145        5      active sync   /dev/sdj1
       6       8      193        6      active sync   /dev/sdm1
       7       8      113        7      active sync   /dev/sdh1
       8       8       81        8      active sync   /dev/sdf1
       9       8      129        9      active sync   /dev/sdi1
      10       8       97       10      active sync   /dev/sdg1
      11       8       33       11      active sync   /dev/sdc1
      12       8       49       12      active sync   /dev/sdd1
      13       8       65       13      active sync   /dev/sde1
      15       8       17       14      active sync   /dev/sdb1
      22      65       81       15      active sync   /dev/sdv1
      21      65       65       16      active sync   /dev/sdu1
      20      65       49       17      active sync   /dev/sdt1
      19      65       33       18      active sync   /dev/sds1
      18      65       17       19      active sync   /dev/sdr1
      17      65        1       20      active sync   /dev/sdq1

      16       8        1        -      spare   /dev/sda1

""".strip()

MDADM_D_CONTENT_MD1 = """
/dev/md1:
          Version : 1.2
      Raid Level : raid5
    Total Devices : 4
      Persistence : Superblock is persistent

            State : inactive
  Working Devices : 4

            Name : any:0
            UUID : 245e1231:245e1231:245e1231:245e1231
          Events : 402

  Number   Major   Minor   RaidDevice

      -     259       16        -        /dev/nvme0n1p1
      -     259       11        -        /dev/nvme1n1p1
      -     259        6        -        /dev/nvme2n1p1
      -     259        1        -        /dev/nvme3n1p1
""".strip()

MDADM_D_CONTENT_MD2 = """
/dev/md2:
           Version : 1.2
     Creation Time : Sun Sep  5 23:19:18 2021
        Raid Level : raid1
        Array Size : 7501333824 (7153.83 GiB 7681.37 GB)
     Used Dev Size : 7501333824 (7153.83 GiB 7681.37 GB)
      Raid Devices : 2
     Total Devices : 2
       Persistence : Superblock is persistent

     Intent Bitmap : Internal

       Update Time : Sun Sep 26 22:18:13 2021
             State : clean
    Active Devices : 2
   Working Devices : 2
    Failed Devices : 0
     Spare Devices : 0

Consistency Policy : bitmap

              Name : hostname:2  (local to host hostname)
              UUID : 245e1231:245e1231:245e1231:245e1231
            Events : 1821

    Number   Major   Minor   RaidDevice State
       0     259        1        0      active sync   /dev/nvme2n1
       1     259        0        1      active sync   /dev/nvme3n1
""".strip()

MDADM_D_CONTENT_MULTI_DEVICES = """
mdadm: cannot open /dev/md0: No such file or directory
/dev/md21:
           Version : 1.2
     Creation Time : Thu Jun 17 09:03:18 2021
        Raid Level : raid1
        Array Size : 43239552 (41.24 GiB 44.28 GB)
     Used Dev Size : 43239552 (41.24 GiB 44.28 GB)
      Raid Devices : 2
     Total Devices : 2
       Persistence : Superblock is persistent
     Intent Bitmap : Internal

       Update Time : Mon Dec  6 14:25:25 2021
             State : clean
    Active Devices : 2
   Working Devices : 2
    Failed Devices : 0
     Spare Devices : 0

Consistency Policy : bitmap

              Name : dvrhdbi3s01:3  (local to host dvrhdbi3s01)
              UUID : 245e1231:245e1231:245e1231:245e1231
            Events : 251

    Number   Major   Minor   RaidDevice State
       0      94       33        0      active sync   /dev/dasdi1
       1      94       53        1      active sync   /dev/dasdn1
mdadm: cannot open /dev/md2: No such file or directory
some continue message of last line
/dev/md22:
           Version : 1.2
     Creation Time : Sun Jun 27 19:14:00 2021
        Raid Level : raid1
        Array Size : 43239552 (41.24 GiB 44.28 GB)
     Used Dev Size : 43239552 (41.24 GiB 44.28 GB)
      Raid Devices : 2
     Total Devices : 2
       Persistence : Superblock is persistent

       Update Time : Sun Dec  5 01:34:48 2021
             State : clean
    Active Devices : 2
   Working Devices : 2
    Failed Devices : 0
     Spare Devices : 0

Consistency Policy : resync

              Name : dvrhdbi3s01:6  (local to host dvrhdbi3s01)
              UUID : 245e1231:245e1231:245e1231:245e1232
            Events : 95

    Number   Major   Minor   RaidDevice State
       0      94       29        0      active sync   /dev/dasdh1
       1      94       37        1      active sync   /dev/dasdj1
mdadm: cannot open /dev/md3: No such file or directory
""".strip()


def test_mdadm_d():
    mds = MDAdmDetail(context_wrap(MDADM_D_CONTENT_MD0, path='insights_commands/mdadm_-D_.dev.md'))
    assert len(mds) == 1
    md = mds[0]
    assert md.device_name == '/dev/md0'
    assert md['device_name'] == '/dev/md0'
    assert md['Update Time'] == 'Sat May 13 07:21:53 2023'
    assert md['Intent Bitmap'] == 'Internal'
    assert md.is_internal_bitmap is True
    assert len(md.device_table) == 22
    assert md.device_table[0] == {'Major': '8',
                                    'Minor': '225',
                                    'Number': '0',
                                    'RaidDevice': '0',
                                    'State': 'active sync   /dev/sdo1'}
    assert md.device_table[-1] == {'Major': '8',
                                    'Minor': '1',
                                    'Number': '16',
                                    'RaidDevice': '-',
                                    'State': 'spare   /dev/sda1'}

    mds = MDAdmDetail(context_wrap(MDADM_D_CONTENT_MD1))
    assert len(mds) == 1
    md = mds[0]
    assert md.device_name == '/dev/md1'
    assert md['State'] == 'inactive'
    assert md['Working Devices'] == '4'
    assert md.is_internal_bitmap is False
    assert len(md.device_table) == 4
    assert md.device_table[0] == {'Major': '259',
                                    'Minor': '16',
                                    'Number': '-',
                                    'RaidDevice': '-        /dev/nvme0n1p1'}

    mds = MDAdmDetail(context_wrap(MDADM_D_CONTENT_MD2))
    assert len(mds) == 1
    md = mds[0]
    assert md.device_name == '/dev/md2'
    assert md['State'] == 'clean'
    assert md['Working Devices'] == '2'
    assert md.is_internal_bitmap is True
    assert len(md.device_table) == 2
    assert md.device_table[0] == {'Major': '259',
                                    'Minor': '1',
                                    'Number': '0',
                                    'RaidDevice': '0',
                                    'State': 'active sync   /dev/nvme2n1'}

    mds = MDAdmDetail(context_wrap(MDADM_D_CONTENT_MULTI_DEVICES))
    assert len(mds) == 2
    assert len(mds.unparsable_device_list) == 0
    md = mds[0]
    assert md.device_name == '/dev/md21'
    assert len(md) == 21
    assert md['State'] == 'clean'
    assert md['Consistency Policy'] == 'bitmap'
    assert md.is_internal_bitmap is True
    assert len(md.device_table) == 2
    md = mds[1]
    assert md.device_name == '/dev/md22'
    assert md['State'] == 'clean'
    assert md['Consistency Policy'] == 'resync'
    assert md.is_internal_bitmap is False
    assert len(md.device_table) == 2
    assert len(mds.error_messages) == 3
    assert mds.error_messages[-1] == "mdadm: cannot open /dev/md3: No such file or directory"


MDADM_D_CONTENT_EMPTY_TABLE = """
/dev/md123:
           Version : 1.2
     Creation Time : Sun Sep  5 23:19:18 2021
        Raid Level : raid1

    Number   Major   Minor   RaidDevice State
""".strip()

MDADM_D_CONTENT_NO_TABLE = """
/dev/md124:
           Version : 1.2
     Creation Time : Sun Sep  5 23:19:18 2021
        Raid Level : raid1

""".strip()

MDADM_D_CONTENT_NO_DETAIL_LIST = """
/dev/md125:
    Number   Major   Minor   RaidDevice State
       0     259        1        0      active sync   /dev/nvme2n1
       1     259        0        1      active sync   /dev/nvme3n1

""".strip()

MDADM_D_CONTENT_EMPTY_DATA_1 = """
/dev/md126:

    Number   Major   Minor   RaidDevice State

""".strip()

MDADM_D_CONTENT_EMPTY_DATA_2 = """
/dev/md127:

""".strip()

MDADM_D_CONTENT_NO_MD_DEVICES = """
mdadm: cannot open /dev/md*: No such file or directory
""".strip()


def test_mdadm_d_special_cases():
    mds = MDAdmDetail(context_wrap('\n'.join([
                        MDADM_D_CONTENT_EMPTY_TABLE,
                        MDADM_D_CONTENT_EMPTY_DATA_1,
                        MDADM_D_CONTENT_NO_TABLE,
                        MDADM_D_CONTENT_EMPTY_DATA_2,
                        MDADM_D_CONTENT_NO_DETAIL_LIST])))

    md = mds[0]
    assert md.device_name == '/dev/md123'
    assert len(md) == 5
    assert md['Raid Level'] == 'raid1'
    assert md.device_table == []
    assert len(md.device_table) == 0

    md = mds[1]
    assert md.device_name == '/dev/md124'
    assert len(md) == 5
    assert md['Raid Level'] == 'raid1'
    assert len(md.device_table) == 0

    md = mds[2]
    assert md.device_name == '/dev/md125'
    assert len(md) == 2
    assert 'Raid Level' not in md
    assert len(md.device_table) == 2

    assert len(mds.unparsable_device_list) == 2
    mds.unparsable_device_list == ['/dev/md126', '/dev/md127']


def test_mdadm_d_exceptions():
    with pytest.raises(SkipComponent) as exc:
        MDAdmDetail(context_wrap(""))
    assert 'Empty content of command output' in str(exc)

    with pytest.raises(SkipComponent) as exc:
        MDAdmDetail(context_wrap("\n"))
    assert 'Empty content of command output' in str(exc)

    with pytest.raises(SkipComponent) as exc:
        MDAdmDetail(context_wrap('\n'.join([
                      MDADM_D_CONTENT_EMPTY_DATA_1,
                      MDADM_D_CONTENT_EMPTY_DATA_2])))
    assert 'Empty parsed device' in str(exc)


def test_doc_examples():
    env = {
        'mdadm': MDAdmMetadata(context_wrap(
            MDADM_CONTENT, path='insights_commands/mdadm_-E_.dev.loop0'
        )),
        'mdadm_d': MDAdmDetail(context_wrap('\n'.join([MDADM_D_CONTENT_MD2, MDADM_D_CONTENT_MD1])))
    }
    failed, total = doctest.testmod(mdadm, globs=env)
    assert failed == 0
