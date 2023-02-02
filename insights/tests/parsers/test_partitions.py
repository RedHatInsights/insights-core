import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import partitions
from insights.parsers.partitions import Partitions
from insights.tests import context_wrap


PARTITIONS_CONTENT = """
major minor  #blocks  name

   8       16 1384120320 sdb
   8        0    3701760 sda
   8       32 2621440000 sdc

 253        0 1384120320 dm-0
   8       48 2726297600 sdd
 253        1 2621440000 dm-1
   8       64 1384120320 sde
 253        2 2726297600 dm-2
   8       96 2621440000 sdg
   8       80   52428800 sdf
   8      112 2726297600 sdh
   8      128  209715200 sdi
   8      144 1384120320 sdj
 253        3   52428800 dm-3
 253        4  209715200 dm-4
   8      160 1384120320 sdk
   8      176 2621440000 sdl
   8      192 2621440000 sdm
 253        5    1048576 dm-5
 253        6   51379200 dm-6
   8      224 2726297600 sdo
   8      208 2726297600 sdn
   8      240   52428800 sdp
  65        0   52428800 sdq
  65       16  209715200 sdr
  65       32  209715200 sds
  65       48   52428800 sdt
  65       64  209715200 sdu
 253        7   15728640 dm-7
 253        8   16777216 dm-8
 253        9   31457280 dm-9
 253       10   10485760 dm-10
 253       11    4194304 dm-11
 253       12  104857600 dm-12
 253       13    5242880 dm-13
 253       14    6287360 dm-14
 253       15    3145728 dm-15
 253       16 2726281216 dm-16
 253       17 1069531136 dm-17
""".strip()

INVALID_PARTITIONS_CONTENT = """
major minor  #blocks  name

   8       16 1384120320
   8        0    3701760 sda
   8       32 2621440000 sdc
""".strip()

EMPTY_CONTENT = """
""".strip()

SAMPLE_INPUT = """
major minor  #blocks  name

   3     0   19531250 hda
   3     1     104391 hda1
   3     2   19422585 hda2
 253     0   22708224 dm-0
 253     1     524288 dm-1
""".strip()


def test_partitions():
    info = Partitions(context_wrap(PARTITIONS_CONTENT))
    assert 'dm-2' in info
    dm_2 = info['dm-2']
    assert dm_2.get('major') == '253'
    assert dm_2.get('minor') == '2'
    assert dm_2.get('blocks') == '2726297600'
    assert 'dm-18' not in info
    p_list = [i for i in info]
    assert p_list[2] in info
    assert len(p_list) == 39
    assert info['dm-17'] == {'major': '253', 'minor': '17', 'blocks': '1069531136', 'name': 'dm-17'}


def test_partitions_invalid_data():
    output = Partitions(context_wrap(INVALID_PARTITIONS_CONTENT))
    assert len(output) == 2
    assert 'sda' in output
    assert 'sdc' in output


def test_empty_content():
    with pytest.raises(SkipComponent) as exc:
        Partitions(context_wrap(EMPTY_CONTENT))
    assert 'Empty content' in str(exc)


def test_partitions_doc_examples():
    env = {'partitions_info': Partitions(context_wrap(SAMPLE_INPUT))}
    failed, total = doctest.testmod(partitions, globs=env)
    assert failed == 0
