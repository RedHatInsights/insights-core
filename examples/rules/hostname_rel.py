#!/usr/bin/env python
"""
Hostname Release
================

This is a simple rule and can be run against the local host
using the following command::

    $ insights-run -p examples.rules.hostname_rel

or from the examples/rules directory::

    $ ./hostname_rel.py
"""
from insights.core.plugins import make_fail, make_pass, rule
from insights.parsers.hostname import Hostname
from insights.parsers.redhat_release import RedhatRelease

ERROR_KEY_1 = "RELEASE_IS_RHEL"
ERROR_KEY_2 = "RELEASE_IS_NOT_RECOGNIZED"
ERROR_KEY_3 = "RELEASE_CANNOT_BE_DETERMINED"

CONTENT = {
    ERROR_KEY_1: "This release is RHEL\nHostname: {{ hostname }}\nRelease: {{ release }}",
    ERROR_KEY_2: "This release is not RHEL\nHostname: {{ hostname }}\nRelease: {{ release }}",
    ERROR_KEY_3: "This release is not RHEL\nHostname: {{ hostname }}\nRelease: not present"
}


@rule(Hostname, [RedhatRelease])
def report(hostname, release):
    if release and release.is_rhel:
        return make_pass(ERROR_KEY_1,
                         hostname=hostname.fqdn,
                         release=release.version)
    elif release:
        return make_fail(ERROR_KEY_2,
                         hostname=hostname.fqdn,
                         release=release.raw)
    else:
        return make_fail(ERROR_KEY_3, hostname=hostname.fqdn)


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
