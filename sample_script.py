#!/usr/bin/env python
from insights.core.plugins import make_response, rule
from insights.combiners.hostname import hostname
from insights.parsers.redhat_release import RedhatRelease

CONTENT = {
    "IS_FEDORA": "{{hn}} runs {{product}}.",
    "IS_NOT_FEDORA": "{{hn}} runs {{product}}."
}


@rule(RedhatRelease, hostname)
def report(rel, hn):
    """Reports whether the machine is running Fedora."""

    if "Fedora" in rel.product:
        return make_response("IS_FEDORA", product=rel.product, hn=hn.fqdn)
    return make_response("IS_NOT_FEDORA", product=rel.product, hn=hn.fqdn)


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
