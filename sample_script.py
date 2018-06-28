#!/usr/bin/env python
from insights.core.plugins import make_response, rule
from insights.parsers.redhat_release import RedhatRelease

CONTENT = {
    "IS_FEDORA": "This machine runs {{product}}.",
    "IS_NOT_FEDORA": "This machine runs {{product}}."
}


@rule(RedhatRelease)
def report(rel):
    """Fires if the machine is running Fedora."""

    if "Fedora" in rel.product:
        return make_response("IS_FEDORA", product=rel.product)
    else:
        return make_response("IS_NOT_FEDORA", product=rel.product)


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
