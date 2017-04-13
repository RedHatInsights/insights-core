from falafel.mappers.ceph_cmd_json_parsing import CephOsdDump, CephOsdDf, CephS, CephECProfileGet, CephCfgInfo, CephHealthDetail
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

CEPH_HEALTH_DETAIL_INFO = """
{
    "health": {
    },
    "timechecks": {
        "epoch": 4,
        "round": 0,
        "round_status": "finished"
    },
    "summary": [],
    "overall_status": "HEALTH_OK",
    "detail": []
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

CEPHINFO = """
{
    "name": "osd.1",
    "cluster": "ceph",
    "debug_none": "0\/5",
    "heartbeat_interval": "5",
    "heartbeat_file": "",
    "heartbeat_inject_failure": "0",
    "perf": "true",
    "max_open_files": "131072",
    "ms_type": "simple",
    "ms_tcp_nodelay": "true",
    "ms_tcp_rcvbuf": "0",
    "ms_tcp_prefetch_max_size": "4096",
    "ms_initial_backoff": "0.2",
    "ms_max_backoff": "15",
    "ms_crc_data": "true",
    "ms_crc_header": "true",
    "ms_die_on_bad_msg": "false",
    "ms_die_on_unhandled_msg": "false",
    "ms_die_on_old_message": "false",
    "ms_die_on_skipped_message": "false",
    "ms_dispatch_throttle_bytes": "104857600",
    "ms_bind_ipv6": "false",
    "ms_bind_port_min": "6800",
    "ms_bind_port_max": "7300",
    "ms_bind_retry_count": "3",
    "ms_bind_retry_delay": "5"
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


class TestCephCfgInfo():
    def test_cephcfginfo(self):
        result = CephCfgInfo(context_wrap(CEPHINFO))

        assert result.data == {
            'ms_tcp_nodelay': 'true', 'ms_max_backoff': '15',
            'cluster': 'ceph', 'ms_dispatch_throttle_bytes': '104857600',
            'debug_none': '0/5', 'ms_crc_data': 'true', 'perf': 'true',
            'ms_tcp_prefetch_max_size': '4096', 'ms_die_on_bad_msg': 'false',
            'ms_bind_port_max': '7300', 'ms_bind_port_min': '6800',
            'ms_die_on_skipped_message': 'false', 'heartbeat_file': '',
            'heartbeat_interval': '5', 'heartbeat_inject_failure': '0',
            'ms_crc_header': 'true', 'max_open_files': '131072',
            'ms_die_on_old_message': 'false', 'name': 'osd.1',
            'ms_type': 'simple', 'ms_initial_backoff': '0.2',
            'ms_bind_retry_delay': '5', 'ms_bind_ipv6': 'false',
            'ms_die_on_unhandled_msg': 'false', 'ms_tcp_rcvbuf': '0',
            'ms_bind_retry_count': '3'
        }

        assert result.max_open_files == '131072'


class TestCephHealthDetail():
    def test_ceph_health_detail(self):
        result = CephHealthDetail(context_wrap(CEPH_HEALTH_DETAIL_INFO)).data

        assert result == {
            "health": {
            },
            "timechecks": {
                "epoch": 4,
                "round": 0,
                "round_status": "finished"
            },
            "summary": [],
            "overall_status": "HEALTH_OK",
            "detail": []
        }
        assert result['overall_status'] == 'HEALTH_OK'
