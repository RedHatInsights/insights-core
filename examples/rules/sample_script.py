#!/usr/bin/env python
"""
Sample Rule
===========

This is a simple rule and can be run against the local host
using the following command::

    $ insights-run -p examples.rules.sample_script

or from the examples/rules directory::

    $ ./sample_rules.py
"""
from insights.core.plugins import make_fail, make_pass, rule
from insights.parsers.redhat_release import RedhatRelease

# Jinga template for message to be displayed for either
# response tag
CONTENT = "This machine runs {{product}}."


@rule(RedhatRelease, content=CONTENT)
def report(rel):
    """Fires if the machine is running Fedora."""

    if "Fedora" in rel.product:
        return make_pass("IS_FEDORA", product=rel.product)
    else:
        return make_fail("IS_NOT_FEDORA", product=rel.product)


if __name__ == "__main__":
    from insights import run
    run(report, print_summary=True)
