#!/usr/bin/env python

import logging
from pprint import pprint

from insights.core import dr
from insights.core.context import HostContext
from insights.core.plugins import make_response, rule
from insights.core.spec_factory import SpecFactory
from insights.parsers.redhat_release import RedhatRelease

logging.basicConfig(level=logging.DEBUG)
sf = SpecFactory()

release = sf.simple_file("/etc/redhat-release", name="release", alias="redhat-release")
"""datasource with alias that matches the parser dependency."""


# You could have the rule depend directly on release if you wanted to, but this
# takes advantage of our RedhatRelease parser since we defined an alias
# on release above to be the same as what the parser depends on.
@rule([RedhatRelease])
def report(broker):
    """Fires if the machine is running Fedora."""

    if "Fedora" in broker[RedhatRelease].product:
        return make_response("IS_FEDORA")


# This sets stuff up and runs on the host system
ctx = HostContext(None)
broker = dr.Broker()
broker[HostContext] = ctx
broker = dr.run(broker=broker)

print "Missing Dependencies:"
pprint(dict(broker.missing_dependencies))

print
print "Exceptions:"
pprint(dict(broker.exceptions))

print
print "Instances:"
pprint(broker.instances)

print
print "Value of release:"
pprint(broker[release].content)

print
print "Value of the rule:"
pprint(broker[report])
