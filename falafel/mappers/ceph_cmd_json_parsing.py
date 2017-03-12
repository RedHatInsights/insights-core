"""
ceph commands with json-pretty para - Command
=============================================

This module provides processing for the output of the ceph related
commands with `-f json-pretty` parameter.

e.g

1. ceph osd dump -f json-pretty

2. ceph osd df -f json-pretty

3. ceph -s -f json-pretty

...


Since all of the commands above have similar json pattern, so
we could define a base class to implement shared code.

Part of the sample output of this command looks like::

    1. `ceph osd dump -f json-pretty`:

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
                "pg_num": 256,
            }
        ]

    ...

    ...

    }


    2. `ceph osd df -f json-pretty`:

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


    3. `ceph -s -f json-pretty`

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
        ...
        ...
        ...

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
        },

        ...

        ...
            }

        }

    }

}


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
    >>> from falafel.mappers.ceph_cmd_json_parsing import CephOsdDump
    >>> from falafel.tests import context_wrap
    >>> shared = {CephOsdDump: CephOsdDump(context_wrap(ceph_osd_dump_content))}
    >>> result = CephOsdDump(context_wrap(ceph_osd_dump_content)).data
    >>> result['pools'][0]['min_size']
    2

    ...

    >>> ceph_osd_dump_content = ''.strip()
    >>> from falafel.mappers.ceph_cmd_json_parsing import CephOsdDf
    >>> from falafel.tests import context_wrap
    >>> shared = {CephOsdDf: CephOsdDf(context_wrap(ceph_osd_df_content))}
    >>> result = CephOsdDf(context_wrap(ceph_osd_df_content)).data
    >>> result['nodes'][0]['pgs']
    945

    ...

    >>> ceph_s_content = ''.strip()
    >>> result = CephS(context_wrap(ceph_s_content)).data
    >>> result['pgmap']['pgs_by_state'][0]['state_name']
    'active+clean'
"""

import json
from .. import Mapper, mapper


class CephJsonParsing(Mapper):
    """Base class implementing shared code."""

    def parse_content(self, content):
        """
        Parse the output of the ceph related commands in Json pattern.

        ceph commands with `-f json-pretty` para will

        """
        self.data = json.loads(''.join(content))
        return


@mapper("ceph_osd_dump")
class CephOsdDump(CephJsonParsing):
    """
    Class to parse the output of ``ceph osd dump -f json-pretty``.
    """
    pass


@mapper("ceph_osd_df")
class CephOsdDf(CephJsonParsing):
    """
    Class to parse the output of ``ceph osd df -f json-pretty``.
    """
    pass


@mapper("ceph_s")
class CephS(CephJsonParsing):
    """
    Class to parse the output of ``ceph -s -f json-pretty``.
    """
    pass
