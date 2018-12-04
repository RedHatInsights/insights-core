"""
Allow users to interrogate components.

``insights-info foo bar baz`` will search for all datasources that might handle
foo, bar, or baz files or commands along with all components that could be
activated if they were present and valid.

``insights-info -i insights.specs.Specs.hosts`` will display dependency
information about the hosts datasource. There are several other options to
the script. ``insights-info -h`` for more info.
"""
from __future__ import print_function
import argparse
import importlib
import inspect
import logging
import pydoc
import re
import sys

from six.moves import StringIO

from insights import dr, get_filters
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
    p.add_argument("paths", nargs="*", help="Files or commands to use for component activation.")
    p.add_argument("-c", "--components", help="Comma separated list of components that have already executed. Names without '.' are assumed to be in insights.specs.Specs.")
    p.add_argument("-i", "--info", help="Comma separated list of components to get dependency info about.", action="store_true")
    p.add_argument("-p", "--preload", help="Comma separated list of packages or modules to preload.")
    p.add_argument("-d", "--pydoc", help="Show pydoc for the given object. E.g.: insights-info -d insights.rule")
    p.add_argument("-s", "--source", help="Show source for the given object. E.g.: insights-info -s insights.core.plugins.rule")
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
        return d.path.strip("/").startswith(path.strip("/"))

    if isinstance(d, sf.glob_file):
        return any(re.match(glob2re(pat), path) and not d.ignore_func(path) for pat in d.patterns)

    if isinstance(d, sf.simple_command):
        return path.strip("/") in d.cmd.strip("/")

    if isinstance(d, sf.first_file):
        return any(p.strip("/").startswith(path.strip("/")) for p in d.paths)

    if isinstance(d, sf.foreach_execute):
        return path.strip("/") in d.cmd.strip("/")

    if isinstance(d, sf.foreach_collect):
        return d.path.strip("/").startswith(path.strip("/")) and not d.ignore_func(path)


def get_matching_datasources(paths):
    if not paths:
        return []
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


def dump_ds(d, space=""):
    dbl_space = space * 2
    delegate = dr.get_delegate(d)
    try:
        print(space + "Class: %s" % d.__class__)
    except:
        pass

    try:
        print(space + "Filtered: %s" % delegate.filterable)
    except:
        pass

    print(space + "Raw: %s" % delegate.raw)
    print(space + "Multioutput: %s" % delegate.multi_output)

    if isinstance(d, sf.simple_file):
        print(space + "Path: %s" % d.path)

    if isinstance(d, (sf.simple_command, sf.foreach_execute)):
        print(space + "Command: %s" % d.cmd)

    if isinstance(d, sf.first_file):
        print(space + "Paths:")
        for p in d.paths:
            print(dbl_space + p)

    if isinstance(d, sf.glob_file):
        print(space + "Patterns:")
        for p in d.patterns:
            print(dbl_space + p)
        print(space + "Ignore: %s" % d.ignore)

    if isinstance(d, sf.foreach_collect):
        print(space + "Path: %s" % d.path)
        print(space + "Ignore: %s" % d.ignore)

    filters = get_filters(d)
    if filters:
        print(space + "Filters:")
        for f in filters:
            print(dbl_space + f)


def print_component(comp, verbose=False):
    print(dr.get_name(comp))

    if not verbose:
        return

    space = " " * 4
    dbl_space = space * 2

    d = dr.get_delegate(comp)
    print(space + "Type: %s" % dr.get_name(d.type))
    if is_type(comp, datasource):
        dump_ds(comp, space=space)

    print()
    if d.requires:
        print(space + "Requires:")
        for r in d.requires:
            print(dbl_space + dr.get_name(r))
    else:
        print(space + "Requires: nothing")

    if d.at_least_one and d.at_least_one[0]:
        for one in d.at_least_one:
            print(space + "At least one of:")
            for o in one:
                print(dbl_space + dr.get_name(o))

    if d.optional:
        print(space + "Optional:")
        for r in d.optional:
            print(dbl_space + dr.get_name(r))

    dependents = dr.get_dependents(comp)
    if dependents:
        print(space + "Dependents:")
        for r in sorted(dependents, key=dr.get_name):
            print(dbl_space + dr.get_name(r))
    print()


def print_results(results, types, verbose):
    for r in results:
        if not types or is_type(r, types):
            print_component(r, verbose=verbose)


def dump_info(comps):
    for c in comps:
        comp = dr.get_component(c)
        if not comp:
            print("Unknown component: %s" % c)
        else:
            print_component(comp, verbose=True)


def load_obj(spec):
    try:
        return dr.get_component(spec) or importlib.import_module(spec)
    except:
        pass


def get_source(spec):
    obj = load_obj(spec)
    if obj:
        return inspect.getsource(obj)


def get_pydoc(spec):
    obj = load_obj(spec)
    if obj:
        output = StringIO()
        pydoc.Helper(output=output).help(obj)
        output.seek(0)
        return output.read()


def main():
    if "" not in sys.path:
        sys.path.insert(0, "")

    args = parse_args()

    if args.source:
        src = get_source(args.source)
        print(src or "{} has no python source.".format(args.source))
        return

    if args.pydoc:
        doc = get_pydoc(args.pydoc)
        print(doc or "{} has no pydoc.".format(args.pydoc))
        return

    load_default_components()
    preload_components(args.preload)

    if args.info:
        dump_info(args.paths)
        return

    types = get_components(args.types, "insights.core.plugins")

    components = get_components(args.components, "insights.specs.Specs")
    ds = get_matching_datasources(args.paths)

    broker = create_broker(components + ds)
    results = dry_run(broker=broker)

    print_results(results, tuple(types), args.verbose)


if __name__ == "__main__":
    main()
