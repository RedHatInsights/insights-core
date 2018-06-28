"""
Ceph status commands
====================

This module provides processing for the output of the following ceph related
commands with `-f json-pretty` parameter.

CephOsdDump - command ``ceph osd dump -f json-pretty``
------------------------------------------------------

CephOsdDf - command ``ceph osd df -f json-pretty``
--------------------------------------------------

CephS - command ``ceph -s -f json-pretty``
------------------------------------------

CephDfDetail - command ``ceph osd erasure-code-profile get default -f json-pretty``
-----------------------------------------------------------------------------------

CephHealthDetail - command ``ceph daemon {ceph_socket_files} config show``
--------------------------------------------------------------------------

CephECProfileGet - command ``ceph health detail -f json-pretty``
----------------------------------------------------------------

CephCfgInfo - command ``ceph df detail -f json-pretty``
-------------------------------------------------------

CephOsdTree - command ``ceph osd tree -f json-pretty``
------------------------------------------------------

All these parsers are based on a shared class which processes the JSON
information into a dictionary.
"""

from .. import JSONParser, parser, CommandParser
from insights.specs import Specs


@parser(Specs.ceph_osd_dump)
class CephOsdDump(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph osd dump -f json-pretty``.

    Examples:

    >>> ceph_osd_dump_content = '''
        ... {
        ...     "epoch": 210,
        ...     "fsid": "2734f9b5-2013-48c1-8e96-d31423444717",
        ...     "created": "2016-11-12 16:08:46.307206",
        ...     "modified": "2017-03-07 08:55:53.301911",
        ...     "flags": "sortbitwise",
        ...     "cluster_snapshot": "",
        ...     "pool_max": 12,
        ...     "max_osd": 8,
        ...     "pools": [
        ...         {
        ...             "pool": 0,
        ...             "pool_name": "rbd",
        ...             "flags": 1,
        ...             "flags_names": "hashpspool",
        ...             "type": 1,
        ...             "size": 3,
        ...             "min_size": 2,
        ...             "crush_ruleset": 0,
        ...             "object_hash": 2,
        ...             "pg_num": 256,
        ...         }
        ...     ]
        ... }
        ... '''.strip()

    >>> result = CephOsdDump(context_wrap(ceph_osd_dump_content)).data
    >>> result['pools'][0]['min_size']
    2
    """
    pass


@parser(Specs.ceph_osd_df)
class CephOsdDf(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph osd df -f json-pretty``.

    Examples:

    >>> ceph_osd_dump_content = '''
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
    '''.strip()
    >>> result = CephOsdDf(context_wrap(ceph_osd_df_content)).data
    >>> result['nodes'][0]['pgs']
    945
    """
    pass


@parser(Specs.ceph_s)
class CephS(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph -s -f json-pretty``.

    Examples:

    >>> ceph_s_content = '''
        {
            "health": {
                "health": {
                    "health_services": [
                        {
                            "mons": [
                                {
                                    "name": "dell-per430-22",
                                    "kb_total": 209612800,
                                    "kb_used": 3718628,
                                    "kb_avail": 205894172,
                                    "avail_percent": 98,
                                    "last_updated": "2017-03-10 22:38:25.920794",
                                    "store_stats": {
                                        "bytes_total": 36402550,
                                        "bytes_sst": 17659238,
                                        "bytes_log": 983040,
                                        "bytes_misc": 17760272,
                                        "last_updated": "0.000000"
                                    },
                                    "health": "HEALTH_OK"
                                }]
                            }
                        ]
                    }
                }
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
                "bytes_avail": 8373190385664
                "bytes_total": 8397595996160
            }
        }
    '''.strip()
    >>> result = CephS(context_wrap(ceph_s_content)).data
    >>> result['pgmap']['pgs_by_state'][0]['state_name']
    'active+clean'
    """
    pass


@parser(Specs.ceph_df_detail)
class CephDfDetail(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph df detail -f json-pretty``.

    Examples:

    >>> ceph_df_content = '''
        {
            "stats": {
                "total_bytes": 17113243648,
                "total_used_bytes": 203120640,
                "total_avail_bytes": 16910123008,
                "total_objects": 0
            },
            "pools": [
                {
                    "name": "rbd",
                    "id": 0,
                    "stats": {
                        "kb_used": 0,
                        "bytes_used": 0,
                        "max_avail": 999252180,
                        "objects": 0,
                        "dirty": 0,
                        "rd": 0,
                        "rd_bytes": 0,
                        "wr": 0,
                        "wr_bytes": 0,
                        "raw_bytes_used": 0
                    }
                }
            ]
        }
    '''.strip()
    >>> result = CephDfDetail(context_wrap(ceph_df_content)).data
    >>> result['stats']['total_avail_bytes']
    16910123008
    """
    pass


@parser(Specs.ceph_health_detail)
class CephHealthDetail(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph health detail -f json-pretty``.

    Examples:

    >>> ceph_health_detail_content = '''
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
    '''.strip()
    >>> result = CephHealthDetail(context_wrap(ceph_health_detail_content)).data
    >>> result["overall_status"]
    "HEALTH_OK"
    """
    pass


@parser(Specs.ceph_osd_ec_profile_get)
class CephECProfileGet(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph osd erasure-code-profile get default -f json-pretty``.

    Examples:

    >>> ceph_osd_ec_profile_get_content = '''
        {
            "k": "2",
            "m": "1",
            "plugin": "jerasure",
            "technique": "reed_sol_van"
        }
    '''.strip()
    >>> result = CephECProfileGet(context_wrap(ceph_osd_ec_profile_get_content)).data
    >>> result['k']
    "2"
    """
    pass


@parser(Specs.ceph_config_show)
class CephCfgInfo(CommandParser, JSONParser):
    """
    Class to parse the output of ``ceph daemon .. config show``

    Examples:

    >>> ceph_daemon_config_show = '''
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
    '''.strip()
    >>> ceph_info = CephCfgInfo(context_wrap(ceph_daemon_config_show))
    >>> cpu_info.max_open_files
    '131072'
    """

    @property
    def max_open_files(self):
        """
        str: Return the value of max_open_files
        """
        return self.data["max_open_files"]


@parser(Specs.ceph_osd_tree)
class CephOsdTree(CommandParser, JSONParser):
    """
    Class to parse the output of the command "ceph osd tree -f json-pretty

    Examples:

    >>> ceph_osd_tree_content = '''
    {
    "nodes": [
        {
            "id": -1,
            "name": "default",
            "type": "root",
            "type_id": 10,
            "children": [
                -5,
                -4,
                -3,
                -2
            ]
        },
        {
            "id": -2,
            "name": "dhcp-192-56",
            "type": "host",
            "type_id": 1,
            "children": []
        },
        {
            "id": -3,
            "name": "dhcp-192-104",
            "type": "host",
            "type_id": 1,
            "children": []
        },
        {
            "id": -4,
            "name": "dhcp-192-67",
            "type": "host",
            "type_id": 1,
            "children": []
        },
        {
            "id": -5,
            "name": "localhost",
            "type": "host",
            "type_id": 1,
            "children": [
                1,
                3,
                5,
                2,
                4,
                0
            ]
        }
    ],
    "stray": []
    }
    '''.strip()
    >>> result = CephOsdTree(context_wrap(ceph_osd_tree_content))
    >>> result['nodes'][0]['children']
    ['-5', '-4', '-3', '-2']
    """
    pass
