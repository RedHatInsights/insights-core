#!/usr/bin/env python
"""
This is a script for collecting output from either the collect.py script
or an archive.
"""

import logging
import sys
from pprint import pprint

from insights.core import dr
from insights.core.hydration import hydrate_new_dir, hydrate_old_archive

log = logging.getLogger(__name__)


def main():
    dr.load_components("insights.parsers")
    dr.load_components("insights.combiners")

    broker = dr.Broker()

    if len(sys.argv) > 1:
        evaluator = hydrate_old_archive(path=sys.argv[1], tmp_dir="/tmp")
    else:
        evaluator = hydrate_new_dir("output")

    evaluator.process()

    broker = evaluator.broker
    pprint(broker.instances)
    pprint(dict(broker.exceptions))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
