#!/usr/bin/env python
from insights.core.plugins import make_response, rule
from insights.parsers.redhat_release import RedhatRelease


@rule(RedhatRelease)
def report(rel):
    """Fires if the machine is running Fedora."""

    if "Fedora" in rel.product:
        return make_response("IS_FEDORA")
    else:
        return make_response("IS_NOT_FEDORA")


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
