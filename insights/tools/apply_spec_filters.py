#!/usr/bin/env python

import json
import os
import re
import sys
import argparse
import logging

from datetime import datetime
from itertools import chain
from collections import OrderedDict

import insights

from insights import load_packages, parse_plugins
from insights.core import dr, filters
from insights.core.spec_factory import RegistryPoint
from insights.specs import Specs

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def load_default_plugins():
    dr.load_components("insights.specs.default")
    dr.load_components("insights.parsers")
    dr.load_components("insights.combiners")


def apply_filters(_format, _plugins, output=None):
    load_default_plugins()

    if _format not in ("yaml", "json"):
        logger.error("Unsupported format: {0}".format(_format))
        return 1

    if not _plugins:
        logger.error("Provide plugins to load.")
        return 1

    load_packages(parse_plugins(_plugins))

    if _format == "yaml":
        yaml_path = output
        if not yaml_path:
            logger.info(
                "Output filters to '{0}'".format(
                    os.path.join(os.path.dirname(insights.__file__), filters._filename)
                )
            )
            filters.dump()
        else:
            logger.info("Output filters to '{0}'".format(yaml_path))
            with open(yaml_path, 'w') as fp:
                filters.dump(fp)

    if _format == "json":
        json_path = output
        if not json_path:
            logger.error("Provide uploader.json location to load and output.")
            return 1

        if not os.path.exists(json_path):
            logger.error("Provided '{0}' path does not exist.".format(json_path))
            return 1

        with open(json_path) as fp:
            uploader_json = json.load(fp, object_pairs_hook=OrderedDict)

        specs = sorted(vars(Specs))
        _filters = {}
        for spec in specs:
            s = getattr(Specs, spec)
            if isinstance(s, RegistryPoint):
                f = filters.get_filters(s)
                if f:
                    _filters[spec] = sorted(f)

        for spec in chain.from_iterable(uploader_json[i] for i in ("commands", "files", "globs")):
            if spec["symbolic_name"] in _filters:
                spec["pattern"] = _filters[spec["symbolic_name"]]

        uploader_json["version"] = datetime.now().isoformat()

        pattern = re.compile(",")
        output = "\n".join(
            pattern.sub(",", l) for l in json.dumps(uploader_json, indent=4).splitlines()
        )

        with open(json_path, "w") as fp:
            fp.write(output)
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--format", help="Filters format.", default="yaml")
    parser.add_argument("-o", "--output", help="Ouput file.", default="")
    parser.add_argument(
        "-p", "--plugins", help="Comma-separated list without spaces of plugins.", default=""
    )
    args = parser.parse_args()

    ret = apply_filters(args.format, args.plugins, args.output)
    sys.exit(ret)


if __name__ == "__main__":
    main()
