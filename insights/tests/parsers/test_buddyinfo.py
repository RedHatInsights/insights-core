from insights.parsers import buddyinfo
from insights.parsers.buddyinfo import BuddyInfo
from insights.core.exceptions import SkipComponent
from insights.tests import context_wrap

import doctest
import pytest

BUDDYINFO_1 = """
Node 0, zone      DMA      0      0      0      0      0      0      0      0      1      1      2
Node 0, zone    DMA32      8     10     12      9      9     11     10     12     12     11    569
Node 0, zone   Normal    460    485    375   1611   3201   2187   1437    844    487    247   6120
Node 1, zone   Normal      1      7   1783   2063   1773   3227   2299   1399    729    430   6723
""".strip()

BUDDYINFO_2 = """
Node 0, zone      DMA      0      0      0      0      1      0      0      1      0      1      2
Node 0, zone    DMA32    890    610    792    663    464    285    128     96    155      9      3
Node 0, zone   Normal  19340   9441   1865    250    163     47      3      3      1      3      0
""".strip()


def test_buddyinfo():
    buddy = BuddyInfo(context_wrap(BUDDYINFO_1))
    assert len(buddy) == 4

    mem = buddy[2]
    assert mem['node'] == '0'
    assert mem['zone'] == 'Normal'
    assert len(mem['counter']) == 11
    assert mem['counter'][10] == 6120
    assert "Node 0, zone   Normal    460    485" in mem['raw']

    mem = buddy[3]
    assert mem['node'] == '1'
    assert mem['zone'] == 'Normal'
    assert mem['counter'][10] == 6723
    assert "Node 1, zone   Normal      1      7" in mem['raw']

    buddy = BuddyInfo(context_wrap(BUDDYINFO_2))
    assert len(buddy) == 3
    assert buddy[0]['counter'][9] == 1

    with pytest.raises(SkipComponent):
        BuddyInfo(context_wrap(""))


def test_doc_examples():
    env = {
        'buddy': BuddyInfo(context_wrap(BUDDYINFO_1))
    }
    failed, total = doctest.testmod(buddyinfo, globs=env)
    assert failed == 0
