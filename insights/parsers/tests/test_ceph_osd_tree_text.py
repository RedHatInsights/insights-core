from insights.parsers import ceph_osd_tree_text, ParseException, SkipException
from insights.parsers.ceph_osd_tree_text import CephOsdTreeText
from insights.tests import context_wrap
import pytest
import doctest

OSD_TREE_CEPH_V3 = """
ID CLASS WEIGHT  TYPE NAME       STATUS REWEIGHT PRI-AFF
-1       0.08752 root default
-9       0.02917     host ceph1
 2   hdd 0.01459         osd.2       up  1.00000 1.00000
 5   hdd 0.01459         osd.5       up  1.00000 1.00000
-5       0.02917     host ceph2
 1   hdd 0.01459         osd.1       up  1.00000 1.00000
 4   hdd 0.01459         osd.4       up  1.00000 1.00000
-3       0.02917     host ceph3
 0   hdd 0.01459         osd.0       up  1.00000 1.00000
 3   hdd 0.01459         osd.3       up  1.00000 1.00000
-7             0     host ceph_1
""".strip()

OSD_TREE_CEPH_V2 = """
ID WEIGHT  TYPE NAME     UP/DOWN REWEIGHT PRIMARY-AFFINITY
-1 0.11670 root default
-2 0.02917     host osd1
 2 0.01459         osd.2      up  1.00000          1.00000
 5 0.01459         osd.5      up  1.00000          1.00000
-3 0.02917     host osd2
 1 0.01459         osd.1      up  1.00000          1.00000
 3 0.01459         osd.3      up  1.00000          1.00000
-4 0.02917     host osd3
 0 0.01459         osd.0      up  1.00000          1.00000
 4 0.01459         osd.4      up  1.00000          1.00000
-5 0.02917     host osd4
 6 0.01459         osd.6    down        0          1.00000
 7 0.01459         osd.7    down        0          1.00000
""".strip()

OSD_TREE_EMPTY = """
""".strip()

OSD_TREE_INVALID = """
ID WEIGHT  UP/DOWN REWEIGHT PRIMARY-AFFINITY
""".strip()


def test_ceph_osd_tree_text_v3():
    ceph_osd_tree = CephOsdTreeText(context_wrap(OSD_TREE_CEPH_V3))
    assert ceph_osd_tree['nodes'][0] == {'id': '-1', 'device_class': '', 'crush_weight': '0.08752', 'name': 'default',
                                         'status': '', 'reweight': '', 'primary_affinity': '', 'type': 'root',
                                         'children': [-7, -3, -5, -9]}


def test_ceph_osd_tree_text_v2():
    ceph_osd_tree = CephOsdTreeText(context_wrap(OSD_TREE_CEPH_V2))
    assert ceph_osd_tree['nodes'][1] == {'id': '-2', 'crush_weight': '0.02917', 'name': 'osd1', 'status': '',
                                         'reweight': '', 'primary_affinity': '', 'type': 'host', 'children': [5, 2]}


def test_skip_content():
    with pytest.raises(SkipException) as e:
        CephOsdTreeText(context_wrap(OSD_TREE_EMPTY))
    assert "Empty content." in str(e)


def test_error_content():
    with pytest.raises(ParseException) as e:
        CephOsdTreeText(context_wrap(OSD_TREE_INVALID))
    assert "Wrong content in table" in str(e)


def test_ceph_osd_tree_text_doc_examples():
    env = {
        'ceph_osd_tree_text': CephOsdTreeText(
            context_wrap(OSD_TREE_CEPH_V3)),
    }
    failed, total = doctest.testmod(ceph_osd_tree_text, globs=env)
    assert failed == 0
