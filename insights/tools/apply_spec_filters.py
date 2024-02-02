#!/usr/bin/env python

import sys

from insights import dr
from insights.core import filters

if len(sys.argv) < 2:
    print("Provide packages to load")
    sys.exit(1)

dr.load_components("insights.specs.default")
dr.load_components("insights.parsers")
dr.load_components("insights.combiners")


for package in sys.argv[2:]:
    dr.load_components(package)

# Default: insights/filters.yaml
filters.dump()
