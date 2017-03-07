"""
ceph osd dump - Command
=======================

This module provides processing for the output of the
``ceph osd dump -f json-pretty`` command.

The specs handled by this command inlude::

    "ceph_osd_dump"             : CommandSpec("/usr/bin/ceph osd dump -f json-pretty"),

Part of the sample output of this command looks like::

    ---
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

    }
    ---

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
    >>> from falafel.mappers.ceph_osd_dump import CephOsdDump
    >>> from falafel.tests import context_wrap
    >>> shared = {CephOsdDump: CephOsdDump(context_wrap(ceph_osd_dump_content))}
    >>> result = CephOsdDump(context_wrap(ceph_osd_dump_content)).data
    >>> result['pools'][0]['min_size']
    2
"""

import json
from .. import Mapper, mapper


@mapper("ceph_osd_dump")
class CephOsdDump(Mapper):
    """
    Parse the output of the command "ceph osd dump -f json-pretty" to get
    a json object
    """
    def parse_content(self, content):
        self.data = json.loads(''.join(content))
        return
