#!/usr/bin/env python

import logging
import os
from pprint import pprint

from insights.core.serde import hydrate, ser

log = logging.getLogger(__name__)


def hydrate_dir(path):
    r = []
    for root, dirs, names in os.walk(path):
        for name in names:
            p = os.path.join(root, name)
            with open(p) as f:
                r.append(hydrate(ser.load(f)))
    return dict(r)


def main():
    pprint(hydrate_dir("output"))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
