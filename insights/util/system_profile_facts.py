#!/usr/bin/env python

from __future__ import print_function

from insights import rule, make_metadata, run

from insights.parsers.meminfo import MemInfo


@rule(
    optional=[
        MemInfo,
    ]
)
def system_profile_facts(
    meminfo
):
    return make_metadata(
        mem_total=meminfo.total if meminfo else None
    )


def get_system_profile_facts(path=None):
    br = run(system_profile_facts, root=path)
    d = br[system_profile_facts]
    del d["type"]
    return d


if __name__ == "__main__":
    import json

    print(json.dumps(get_system_profile_facts()))
