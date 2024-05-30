#!/usr/bin/env python

import json
import os
import re
import sys
from datetime import datetime
from itertools import chain
from collections import OrderedDict
from insights import dr, get_filters
from insights.core.spec_factory import RegistryPoint
from insights.specs import Specs
from insights.core import filters

if len(sys.argv) < 3:
    print("Provide uploader.json location and packages to load")
    sys.exit(1)

json_path = sys.argv[1]

if not os.path.exists(json_path):
    print("Provided uploader.json path does not exist.")
    sys.exit(1)

with open(json_path) as fp:
    uploader_json = json.load(fp, object_pairs_hook=OrderedDict)

dr.load_components("insights.specs.default")
dr.load_components("insights.parsers")
dr.load_components("insights.combiners")


for package in sys.argv[2:]:
    dr.load_components(package)

filters.dump()
specs = sorted(vars(Specs))
filters = {}
for spec in specs:
    s = getattr(Specs, spec)
    if isinstance(s, RegistryPoint):
        f = get_filters(s)
        if f:
            filters[spec] = sorted(f)

for spec in chain.from_iterable(uploader_json[i] for i in ("commands", "files", "globs")):
    if spec["symbolic_name"] in filters:
        spec["pattern"] = filters[spec["symbolic_name"]]

uploader_json["version"] = datetime.now().isoformat()

pattern = re.compile(", $")
output = "\n".join(pattern.sub(",", l) for l in json.dumps(uploader_json, indent=4).splitlines())

with open(json_path, "w") as fp:
    fp.write(output)
