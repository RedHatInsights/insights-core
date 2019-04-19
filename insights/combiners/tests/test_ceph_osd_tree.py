from insights.parsers.ceph_osd_tree_text import CephOsdTreeText
from insights.parsers.ceph_insights import CephInsights
from insights.parsers.ceph_cmd_json_parsing import CephOsdTree as CephOsdTreeParser
from insights.combiners import ceph_osd_tree
from insights.combiners.ceph_osd_tree import CephOsdTree
from insights.tests import context_wrap
import doctest

CEPH_INSIGHTS = """
{
  "osd_tree": {
    "nodes": [
      {
        "children": [
          -3
        ],
        "type_id": 10,
        "type": "root",
        "id": -1,
        "name": "default"
      },
      {
        "name": "daq",
        "type_id": 1,
        "id": -3,
        "pool_weights": {},
        "type": "host",
        "children": [
          2,
          1,
          0
        ]
      },
      {
        "status": "up",
        "name": "osd.0",
        "exists": 1,
        "type_id": 0,
        "reweight": 1.0,
        "crush_weight": 0.009796142578125,
        "pool_weights": {},
        "primary_affinity": 1.0,
        "depth": 2,
        "device_class": "ssd",
        "type": "osd",
        "id": 0
      },
      {
        "status": "up",
        "name": "osd.1",
        "exists": 1,
        "type_id": 0,
        "reweight": 1.0,
        "crush_weight": 0.009796142578125,
        "pool_weights": {},
        "primary_affinity": 1.0,
        "depth": 2,
        "device_class": "ssd",
        "type": "osd",
        "id": 1
      },
      {
        "status": "up",
        "name": "osd.2",
        "exists": 1,
        "type_id": 0,
        "reweight": 1.0,
        "crush_weight": 0.009796142578125,
        "pool_weights": {},
        "primary_affinity": 1.0,
        "depth": 2,
        "device_class": "ssd",
        "type": "osd",
        "id": 2
      }
    ],
    "stray": []
  },
  "osd_metadata": {
    "1": {
      "bluefs_db_size": "67108864",
      "bluestore_bdev_size": "10737418240",
      "bluestore_bdev_driver": "KernelDevice"
    }
  },
  "version": {
    "release": 14,
    "major": 0,
    "full": "ceph version 14.0.0-3517-g5322f99370 (5322f99370d629f6927b9c948522a003fc5da5bb) nautilus (dev)",
    "minor": 0
  }
}
""".strip()

CEPH_OSD_TREE_TEXT = """
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

CEPH_OSD_TREE = """
{
    "nodes": [
        {
            "id": -1,
            "name": "default",
            "type": "root",
            "type_id": 10,
            "children": [
                -7,
                -3,
                -5,
                -9
            ]
        },
        {
            "id": -9,
            "name": "ceph1",
            "type": "host",
            "type_id": 1,
            "pool_weights": {},
            "children": [
                5,
                2
            ]
        },
        {
            "id": 2,
            "device_class": "hdd",
            "name": "osd.2",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.014587,
            "depth": 2,
            "pool_weights": {},
            "exists": 1,
            "status": "up",
            "reweight": 1.000000,
            "primary_affinity": 1.000000
        },
        {
            "id": 5,
            "device_class": "hdd",
            "name": "osd.5",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.014587,
            "depth": 2,
            "pool_weights": {},
            "exists": 1,
            "status": "up",
            "reweight": 1.000000,
            "primary_affinity": 1.000000
        },
        {
            "id": -5,
            "name": "ceph2",
            "type": "host",
            "type_id": 1,
            "pool_weights": {},
            "children": [
                4,
                1
            ]
        },
        {
            "id": 1,
            "device_class": "hdd",
            "name": "osd.1",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.014587,
            "depth": 2,
            "pool_weights": {},
            "exists": 1,
            "status": "up",
            "reweight": 1.000000,
            "primary_affinity": 1.000000
        },
        {
            "id": 4,
            "device_class": "hdd",
            "name": "osd.4",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.014587,
            "depth": 2,
            "pool_weights": {},
            "exists": 1,
            "status": "up",
            "reweight": 1.000000,
            "primary_affinity": 1.000000
        },
        {
            "id": -3,
            "name": "ceph3",
            "type": "host",
            "type_id": 1,
            "pool_weights": {},
            "children": [
                3,
                0
            ]
        },
        {
            "id": 0,
            "device_class": "hdd",
            "name": "osd.0",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.014587,
            "depth": 2,
            "pool_weights": {},
            "exists": 1,
            "status": "up",
            "reweight": 1.000000,
            "primary_affinity": 1.000000
        },
        {
            "id": 3,
            "device_class": "hdd",
            "name": "osd.3",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 0.014587,
            "depth": 2,
            "pool_weights": {},
            "exists": 1,
            "status": "up",
            "reweight": 1.000000,
            "primary_affinity": 1.000000
        },
        {
            "id": -7,
            "name": "ceph_1",
            "type": "host",
            "type_id": 1,
            "pool_weights": {},
            "children": []
        }
    ],
    "stray": []
}
""".strip()


def test_ceph_osd_tree_parser():
    cot = CephOsdTreeParser(context_wrap(CEPH_OSD_TREE))
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    ret = CephOsdTree(cot, ci, None)
    assert ret["nodes"][0] == {'id': -1, 'name': 'default', 'type': 'root', 'type_id': 10, 'children': [-7, -3, -5, -9]}


def test_ceph_osd_tree_parser_2():
    cot = CephOsdTreeParser(context_wrap(CEPH_OSD_TREE))
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    cott = CephOsdTreeText(context_wrap(CEPH_OSD_TREE_TEXT))
    ret = CephOsdTree(cot, ci, cott)
    assert ret["nodes"][0] == {'id': -1, 'name': 'default', 'type': 'root', 'type_id': 10, 'children': [-7, -3, -5, -9]}


def test_ceph_insights():
    ci = CephInsights(context_wrap(CEPH_INSIGHTS))
    cott = CephOsdTreeText(context_wrap(CEPH_OSD_TREE_TEXT))
    ret = CephOsdTree(None, ci, cott)
    assert ret["nodes"][0] == {'children': [-3], 'type_id': 10, 'type': 'root', 'id': -1, 'name': 'default'}


def test_ceph_osd_tree_text():
    cott = CephOsdTreeText(context_wrap(CEPH_OSD_TREE_TEXT))
    ret = CephOsdTree(None, None, cott)
    assert ret["nodes"][0] == {'id': '-1', 'device_class': '', 'crush_weight': '0.08752', 'name': 'default',
                               'status': '', 'reweight': '', 'primary_affinity': '', 'type': 'root',
                               'children': [-7, -3, -5, -9]}


def test_ceph_osd_tree_doc_examples():
    env = {
        'cot': CephOsdTree(None, None, CephOsdTreeText(
            context_wrap(CEPH_OSD_TREE_TEXT)))

    }
    failed, total = doctest.testmod(ceph_osd_tree, globs=env)
    assert failed == 0
