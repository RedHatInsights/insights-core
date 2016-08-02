import argparse
import inspect
import logging
import os
import re
import sys
from collections import defaultdict
from falafel.core import marshalling

DEFAULT_PATTERN = r'.*py$'
log = logging.getLogger(__name__)

DEFAULT_PLUGIN_MODULE = "falafel.plugins"


def load_package(package_name, pattern=None, loaded_map=set()):

    if package_name in loaded_map:
        return

    module_count = 0

    __import__(package_name, globals(), locals(), [], -1)

    for module_name in get_module_names(sys.modules[package_name], pattern):
        __import__(module_name, globals(), locals(), [], -1)
        module_count += 1
        log.debug("loaded %s", module_name)

    loaded_map.add(package_name)
    log.info("Loaded %d modules", module_count)


def get_module_names(package_name, pattern=None):

    if not pattern:
        pattern = DEFAULT_PATTERN

    plugin_matcher = re.compile(pattern)

    def name_filter(name):
        if "__init__" not in name and "__main__" not in name:
            if name.endswith(".py") and plugin_matcher.match(name):
                return True
        return False

    plugin_dir = os.path.dirname(os.path.realpath(package_name.__file__))
    log.debug("looking for files that match: [%s] in [%s]", pattern, plugin_dir)
    for root, dirs, files in os.walk(plugin_dir):
        if os.path.exists(os.path.join(root, "__init__.py")):
            for file_ in files:
                if name_filter(file_):
                    plugin_name, dot, suffix = file_.rpartition(".")
                    if dot == "." and suffix == "py":
                        if get_importable_path(root):
                            yield "%s.%s" % (get_importable_path(root), plugin_name)
                        else:
                            yield plugin_name


def get_importable_path(path):
    """
    Get an importable package from the given path. Will return an absolute
    package path if it exists.

    Works by selecting the most specific (i.e. longest common prefix) possible
    path to import from.
    """
    dirs = map(os.path.realpath, sys.path)
    prefixes = [os.path.commonprefix([path, el]) for el in dirs if path.startswith(el)]
    longest = max(prefixes, key=len)
    if longest:
        return path.replace(longest, '').lstrip('/').replace('/', '.')
    else:
        raise Exception("%s cannot be imported due to an insufficient sys.path" % path)


def computed(f):
    f.computed = True
    return f


class MapperOutput(object):

    def __init__(self, data, path=None):
        self.data = data
        self.computed = {}
        if path:
            self._add_to_computed("file_path", path)
            self._add_to_computed("file_name", os.path.basename(path))
        self.compute()

    def get_name(self):
        return "#".join([self.__module__, self.__class__.__name__])

    def to_json(self):
        return [self.get_name(), self.data, self.computed_to_json()]

    def computed_to_json(self):
        d = {}
        for k, v in self.computed.iteritems():
            d[k] = v.to_json() if isinstance(v, MapperOutput) else v
        return d

    def _add_to_computed(self, key, value):
        self.computed[key] = value
        setattr(self, key, value)

    def compute(self):
        for key, value in inspect.getmembers(self, inspect.ismethod):
            if hasattr(value, "computed"):
                self._add_to_computed(key, value())

    def __getitem__(self, key):
        if isinstance(key, int):
            raise TypeError("MapperOutput does not support integer indexes")
        if key in self.data:
            return self.data[key]
        if key in self.computed:
            return self.computed[key]
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self.data or key in self.computed

    def __eq__(self, item):
        if isinstance(item, MapperOutput):
            return self.data == item.data
        else:
            return False


class ErrorCollector(object):
    errors = defaultdict(lambda: {
        "count": 0,
        "exception": None,
        "func": None
    })

    def reducer_error(self, func, e, local, shared):
        key = "".join([func.__module__, str(type(e)), str(e.message)])
        error = self.errors[key]
        error["count"] = error["count"] + 1
        error["exception"] = e
        error["func"] = func

    def has_errors(self):
        return len(self.errors) > 0

    def format_errors(self):
        for error in self.errors.values():
            e = error["exception"]
            func = error["func"]
            count = error["count"]
            ename = e.__class__.__name__
            yield "%d count(s) of [%s]: %s: %s" % (count, func.__module__, ename, e.message)


def print_result(r, case=None, min_key_len=0):
    if r["type"] == "rule":
        heading = r["error_key"]
        del r["error_key"]
    elif len(r.keys()) == 1:
        return
    else:
        heading = "metadata"
    del r["type"]
    if min_key_len:
        heading = heading.ljust(min_key_len)
    case_prefix = "({0}) ".format(case) if case else ""
    print "%s: %s" % (case_prefix + heading, marshalling.marshal(r))


def print_results(results, cases=None, error_collector=None):
    results.sort(key=lambda x: x[1].__module__)
    min_key_len = max([0] + [len(r["error_key"]) for h, f, r in results if "error_key" in r])
    result_count = len([r for host, f, r in results if "error_key" in r])
    for host, func, r in results:
        case = cases.get(host) if cases else None
        print_result(r, case=case, min_key_len=min_key_len)
    print "Result count:", result_count
    if error_collector and error_collector.has_errors():
        print "\n===== ERRORS ====="
        for error_str in error_collector.format_errors():
            print error_str


def main():
    from falafel.core import mapper, reducer
    HELP = [
        "Pattern used to filter out plugins for execution.",
        "Verbose console logging (n.b. it's *very* verbose).",
        "Only run reducers.  Expect mapper output from stdin.",
        "Only run mappers.  Pipes mapper output to stdout."
    ]
    p = argparse.ArgumentParser("insights-run")
    p.add_argument(
        "-p", "--pattern", dest="pattern", help=HELP[0])
    p.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true",
        default=False, help=HELP[1])
    p.add_argument(
        "-r", "--reduce-only", dest="reduce_only",
        action="store_true", default=False, help=HELP[2])
    p.add_argument(
        "-m", "--map-only", dest="map_only", action="store_true",
        default=False, help=HELP[3])
    p.add_argument("packages", nargs="*")
    args = p.parse_args()
    if len(args.packages) == 0:
        p.print_help()
        print "\nERROR: Please provide at least one plugin package"
        return
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.getLogger(__name__).warning("Loading plugins")
    for package in args.packages:
        load_package(package, pattern=args.pattern)
    log = logging.getLogger("main")
    if args.map_only and args.reduce_only:
        print """
    Cannot specify map_only and reduce_only.
    Don't specify either if you want to both map and reduce
        """.strip()
    elif args.map_only:
        log.warning("Map-only run")
        _, mapper_results = mapper.run(sys.stdin)
        print mapper.serialize(mapper_results)
    elif args.reduce_only:
        mapper_results = reducer.deserialize(sys.stdin.read())
        log.warning("Reduce-only run")
        ec = ErrorCollector()
        results = list(reducer.run(mapper_results, ec.reducer_error))
        print_results(results, error_collector=ec)
    else:
        log.warning("Running mappers")
        cases, mapper_results = mapper.run(sys.stdin)
        log.warning("Running reducers")
        ec = ErrorCollector()
        results = list(reducer.run(mapper_results, ec.reducer_error))
        print_results(results, cases, ec)
