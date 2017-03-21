from falafel.mappers.ceph_cmd_json_parsing import CephOsdDump, CephOsdDf, CephS, CephECProfileGet
from falafel.tests import context_wrap

CEPH_OSD_DUMP_INFO = """
{
    "epoch": 210,
    "fsid": "2734f9b5-2013-48c1-8e96-d31423444717",
    "created": "2016-11-12 16:08:46.307206",
    "modified": "2017-03-07 08:55:53.301911",
    "flags": "sortbitwise",
    "cluster_snapshot": "",
    "pool_max": 12,
    "max_osd": 8,
    "pools": [
        {
            "pool": 0,
            "pool_name": "rbd",
            "flags": 1,
            "flags_names": "hashpspool",
            "type": 1,
            "size": 3,
            "min_size": 2,
            "crush_ruleset": 0,
            "object_hash": 2,
            "pg_num": 256
        }
    ]
}
""".strip()

CEPH_OSD_DF_INFO = """
{
    "nodes": [
        {
            "id": 0,
            "name": "osd.0",
            "type": "osd",
            "type_id": 0,
            "crush_weight": 1.091095,
            "depth": 2,
            "reweight": 1.000000,
            "kb": 1171539620,
            "kb_used": 4048208,
            "kb_avail": 1167491412,
            "utilization": 0.345546,
            "var": 1.189094,
            "pgs": 945
        }
    ],
    "stray": [],
    "summary": {
        "total_kb": 8200777340,
        "total_kb_used": 23831128,
        "total_kb_avail": 8176946212,
        "average_utilization": 0.290596,
        "min_var": 0.803396,
        "max_var": 1.189094,
        "dev": 0.035843
    }
}
""".strip()

CEPH_S_INFO = """
{
    "health": {

    },
    "pgmap": {
        "pgs_by_state": [
            {
                "state_name": "active+clean",
                "count": 1800
            }
        ],
        "version": 314179,
        "num_pgs": 1800,
        "data_bytes": 7943926574,
        "bytes_used": 24405610496,
        "bytes_avail": 8373190385664,
        "bytes_total": 8397595996160
    },
    "fsmap": {
        "epoch": 1,
        "by_rank": []
    }
}
""".strip()

CEPH_OSD_EC_PROFILE_GET = """
{
    "k": "2",
    "m": "1",
    "plugin": "jerasure",
    "technique": "reed_sol_van"
}
""".strip()


class TestCephOsdDump():
    def test_ceph_osd_dump(self):
        result = CephOsdDump(context_wrap(CEPH_OSD_DUMP_INFO)).data

        assert result == {
            'pool_max': 12, 'max_osd': 8,
            'created': '2016-11-12 16:08:46.307206',
            'modified': '2017-03-07 08:55:53.301911',
            'epoch': 210, 'flags': u'sortbitwise',
            'cluster_snapshot': '',
            'fsid': '2734f9b5-2013-48c1-8e96-d31423444717',
            'pools': [
                {
                    'pool_name': 'rbd', 'flags_names': 'hashpspool',
                    'min_size': 2, 'object_hash': 2, 'flags': 1,
                    'pg_num': 256, 'crush_ruleset': 0, 'type': 1,
                    'pool': 0, 'size': 3
                }
            ]
        }
        assert result['pools'][0]['min_size'] == 2


class TestCephOsdDf():
    def test_ceph_osd_df(self):
        result = CephOsdDf(context_wrap(CEPH_OSD_DF_INFO)).data

        assert result == {
            "nodes": [
                {
                    "id": 0,
                    "name": "osd.0",
                    "type": "osd",
                    "type_id": 0,
                    "crush_weight": 1.091095,
                    "depth": 2,
                    "reweight": 1.000000,
                    "kb": 1171539620,
                    "kb_used": 4048208,
                    "kb_avail": 1167491412,
                    "utilization": 0.345546,
                    "var": 1.189094,
                    "pgs": 945
                }
            ],
            "stray": [],
            "summary": {
                "total_kb": 8200777340,
                "total_kb_used": 23831128,
                "total_kb_avail": 8176946212,
                "average_utilization": 0.290596,
                "min_var": 0.803396,
                "max_var": 1.189094,
                "dev": 0.035843
            }
        }
        assert result['nodes'][0]['pgs'] == 945


class TestCephS():
    def test_ceph_s(self):
        result = CephS(context_wrap(CEPH_S_INFO)).data

        assert result == {
            "health": {

            },
            "pgmap": {
                "pgs_by_state": [
                    {
                        "state_name": "active+clean",
                        "count": 1800
                    }
                ],
                "version": 314179,
                "num_pgs": 1800,
                "data_bytes": 7943926574,
                "bytes_used": 24405610496,
                "bytes_avail": 8373190385664,
                "bytes_total": 8397595996160
            },
            "fsmap": {
                "epoch": 1,
                "by_rank": []
            }
        }
        assert result['pgmap']['pgs_by_state'][0]['state_name'] == 'active+clean'


class TestCephECProfileGet():
    def test_ceph_ec_profile_get(self):
        result = CephECProfileGet(context_wrap(CEPH_OSD_EC_PROFILE_GET)).data

        assert result == {
            "k": "2",
            "m": "1",
            "plugin": "jerasure",
            "technique": "reed_sol_van"
        }
        assert result['k'] == "2"
        assert result['m'] == "1"
