#!/usr/bin/env python
"""
Given a list of plugins to load, print a report of any containing rules that
might produce the same result keys.
"""
from __future__ import print_function
import argparse
import inspect
from collections import defaultdict

from insights import dr, parse_plugins, rule


def parse_args():
    p = argparse.ArgumentParser(description="Find rule modules that could produce the same response keys.")
    p.add_argument("-p",
                   "--plugins",
                   default="",
                   help="Comma separated list of package(s) or module(s) containing plugins.")
    return p.parse_args()


def main():
    args = parse_args()

    plugins = parse_plugins(args.plugins)
    for p in plugins:
        dr.load_components(p, continue_on_error=False)

    results = defaultdict(list)
    for comp, delegate in dr.DELEGATES.items():
        if isinstance(delegate, rule):
            results[dr.get_base_module_name(comp)].append(comp)

    results = dict((key, comps) for key, comps in results.items() if len(comps) > 1)

    if results:
        print("Potential key conflicts:")
        print()
        for key in sorted(results):
            print("{key}:".format(key=key))
            for comp in sorted(results[key], key=dr.get_name):
                name = comp.__name__
                path = inspect.getabsfile(comp)
                print("    {name} in {path}".format(name=name, path=path))
            print()


if __name__ == "__main__":
    main()
