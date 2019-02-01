#!/usr/bin/env python
from __future__ import print_function

from insights import make_response, rule, run
from insights.parsers.installed_rpms import InstalledRpms

ERROR_KEY = "TOO_MANY_HOSTS"

CONTENT = {
    ERROR_KEY: """Bash version: {{bash}}"""
}


@rule(InstalledRpms)
def report(rpms):
    bash = rpms.get_max('bash')
    return make_response("TOO_MANY_HOSTS", bash=bash)


if __name__ == "__main__":
    run(report, print_summary=True)
