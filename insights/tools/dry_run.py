"""
Show which components would run given a set that have already executed.
"""
from __future__ import print_function
import argparse
import logging
import re

from insights import dr
from insights.core.plugins import datasource, is_type
from insights.core import spec_factory as sf

logging.basicConfig(level=logging.ERROR)


def glob2re(pat):
    """
    Translate a shell PATTERN to a regular expression.
    There is no way to quote meta-characters.

    Stolen from https://stackoverflow.com/a/29820981/1451664
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:
        c = pat[i]
        i = i + 1
        if c == '*':
            # res = res + '.*'
            res = res + '[^/]*'
        elif c == '?':
            # res = res + '.'
            res = res + '[^/]'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j + 1
            if j < n and pat[j] == ']':
                j = j + 1
            while j < n and pat[j] != ']':
                j = j + 1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\', '\\\\')
                i = j + 1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + '\Z(?ms)'


def parse_args():
    p = argparse.ArgumentParser(__doc__.strip())
    p.add_argument("-p", "--preload", help="Comma separated list of packages or modules to preload.")
    p.add_argument("-f", "--files", help="Comma separated list of paths or commands to match.")
    p.add_argument("-c", "--components", help="Comma separated list of components that have already executed. Names without '.' are assumed to be in insights.specs.Specs.")
    p.add_argument("-t", "--types", help="Filter results based on component type; e.g. 'rule,parser'. Names without '.' are assumed to be in insights.core.plugins.")
    p.add_argument("-v", "--verbose", help="Print component dependencies.", action="store_true")
    return p.parse_args()


def load_default_components():
    default_packages = [
        "insights.specs.default",
        "insights.specs.insights_archive",
        "insights.specs.sos_archive",
        "insights.specs.jdr_archive",
        "insights.parsers",
        "insights.combiners",
    ]

    for p in default_packages:
        dr.load_components(p, continue_on_error=False)


def preload_components(comps):
    if comps:
        for c in comps.split(","):
            dr.load_components(c.strip(), continue_on_error=False)


def get_components(comps, default_module):
    if not default_module.endswith("."):
        default_module = default_module + "."

    results = []
    if comps:
        comps = [t.strip() for t in comps.split(",")]
        comps = [t if "." in t else default_module + t for t in comps]
        for t in comps:
            c = dr.get_component(t)
            if not c:
                raise Exception("Could not load %s." % t)
            results.append(c)
    return results


def get_datasources():
    ds_types = (sf.simple_file,
                sf.glob_file,
                sf.simple_command,
                sf.first_file,
                sf.foreach_execute,
                sf.foreach_collect)
    ds = dr.COMPONENTS_BY_TYPE[datasource]
    return [d for d in ds if isinstance(d, ds_types)]


def matches(d, path):
    if isinstance(d, sf.simple_file):
        return d.path.strip("/") == path.strip("/")

    if isinstance(d, sf.glob_file):
        return any(re.match(glob2re(pat), path) and not d.ignore_func(path) for pat in d.patterns)

    if isinstance(d, sf.simple_command):
        return d.cmd.strip("/") == path.strip("/")

    if isinstance(d, sf.first_file):
        return any(p.strip("/") == path.strip("/") for p in d.paths)

    if isinstance(d, sf.foreach_execute):
        return d.cmd.strip("/").startswith(path.strip("/"))

    if isinstance(d, sf.foreach_collect):
        return d.path.strip("/").startswith(path.strip("/")) and not d.ignore_func(path)


def get_matching_datasources(paths):
    if not paths:
        return []
    paths = [p.strip() for p in paths.split(",")]
    ds = get_datasources()
    results = set()
    for path in paths:
        for d in ds:
            if matches(d, path):
                results.add(d)
    return list(results)


def create_broker(components):
    broker = dr.Broker()
    for c in components:
        broker[c] = 1
    return broker


def dry_run(graph=dr.COMPONENTS[dr.GROUPS.single], broker=None):
    broker = broker or dr.Broker()
    for c in broker.instances:
        yield c
    for c in dr.run_order(graph):
        d = dr.get_delegate(c)
        if d and d.get_missing_dependencies(broker) is None:
            broker[c] = 1
            yield c


def print_component(comp, verbose=False):
    print(dr.get_name(comp))

    if not verbose:
        return

    space = " " * 4
    dbl_space = space * 2

    d = dr.get_delegate(comp)
    if d.requires:
        print(space + "Requires")
        for r in d.requires:
            print(dbl_space + dr.get_name(r))
    else:
        print(space + "Requires nothing")

    if d.at_least_one and d.at_least_one[0]:
        for one in d.at_least_one:
            print(space + "At least one of")
            for o in one:
                print(dbl_space + dr.get_name(o))

    if d.optional:
        print(space + "Optional")
        for r in d.optional:
            print(dbl_space + dr.get_name(r))
    print()


def print_results(results, types, verbose):
    print("Could have run:")
    print()
    for r in results:
        if not types or is_type(r, types):
            print_component(r, verbose=verbose)


def main():
    args = parse_args()

    load_default_components()
    preload_components(args.preload)
    types = get_components(args.types, "insights.core.plugins")

    components = get_components(args.components, "insights.specs.Specs")
    ds = get_matching_datasources(args.files)

    broker = create_broker(components + ds)
    results = dry_run(broker=broker)

    print_results(results, tuple(types), args.verbose)


if __name__ == "__main__":
    main()
