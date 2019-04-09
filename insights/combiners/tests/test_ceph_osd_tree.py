from insights.parsers.ceph_osd_tree_text import CephOsdTreeText
from insights.parsers.ceph_insights import CephInsights
from insights.parsers.ceph_cmd_json_parsing import CephOsdTree as CephOsdTreeParser
from insights.combiners.ceph_osd_tree import CephOsdTree
from insights.tests import context_wrap

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
      "bluestore_bdev_driver": "KernelDevice",
      "bluefs_db_path": "/home/nwatkins/src/ceph/build/dev/osd1/block.db",
      "bluefs_db_rotational": "0",
      "bluefs_db_access_mode": "file",
      "mem_swap_kb": "8097788",
      "bluestore_bdev_type": "ssd",
      "bluefs_wal_size": "1048576000",
      "back_addr": "127.0.0.1:6805/4559",
      "bluefs_db_block_size": "4096",
      "bluefs_single_shared_device": "0",
      "hostname": "daq",
      "distro_version": "28",
      "ceph_release": "nautilus",
      "bluefs_wal_rotational": "0",
      "bluestore_bdev_block_size": "4096",
      "bluefs_db_driver": "KernelDevice",
      "ceph_version": "ceph version Development (no_version) nautilus (dev)",
      "distro": "fedora",
      "bluefs_wal_type": "ssd",
      "journal_rotational": "0",
      "back_iface": "",
      "hb_back_addr": "127.0.0.1:6807/4559",
      "osd_objectstore": "bluestore",
      "rotational": "0",
      "bluestore_bdev_access_mode": "file",
      "bluefs_db_type": "ssd",
      "arch": "x86_64",
      "hb_front_addr": "127.0.0.1:6806/4559",
      "kernel_description": "#1 SMP Mon Sep 10 15:44:45 UTC 2018",
      "bluefs_wal_block_size": "4096",
      "distro_description": "Fedora 28 (Workstation Edition)",
      "front_addr": "127.0.0.1:6804/4559",
      "bluefs_wal_driver": "KernelDevice",
      "front_iface": "",
      "kernel_version": "4.18.7-200.fc28.x86_64",
      "bluefs": "1",
      "bluestore_bdev_rotational": "0",
      "bluefs_wal_path": "/home/nwatkins/src/ceph/build/dev/osd1/block.wal",
      "devices": "dm-2,nvme0n1p2",
      "mem_total_kb": "16066432",
      "default_device_class": "ssd",
      "bluestore_bdev_path": "/home/nwatkins/src/ceph/build/dev/osd1/block",
      "bluefs_wal_access_mode": "file",
      "ceph_version_short": "Development",
      "device_ids": "nvme0n1p2=SAMSUNG_MZVLW256HEHP-000L7_S35ENX1K429295",
      "os": "Linux",
      "cpu": "Intel(R) Core(TM) i7-8650U CPU @ 1.90GHz",
      "osd_data": "/home/nwatkins/src/ceph/build/dev/osd1"
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
