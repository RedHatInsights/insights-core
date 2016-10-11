import argparse
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

    loaded = []

    if package_name in loaded_map:
        return

    __import__(package_name, globals(), locals(), [], -1)

    for module_name in get_module_names(sys.modules[package_name], pattern):
        m = __import__(module_name, globals(), locals(), [package_name], -1)
        loaded.append(m)
        log.debug("loaded %s", module_name)

    loaded_map.add(package_name)
    log.info("Loaded %d modules", len(loaded))
    return loaded


def get_module_names(package_name, pattern=None):

    if not pattern:
        pattern = DEFAULT_PATTERN
    else:
        pattern = '.*' + pattern + '.*'

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
            for file_ in filter(name_filter, files):
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


class Mapper(object):
    """
    Base class designed to be subclassed by mappers.

    The framework will construct your object with a `Context` that will
    provide *at least* the content as an interable of lines and the path
    that the content was retrieved from.

    Facts should be exposed as instance members where applicable.

      self.fact = "123"
    """

    def __init__(self, context):
        self.file_path = context.path
        self.file_name = os.path.basename(context.path) if context.path is not None else None
        self.parse_content(context.content)

    def parse_content(self, content):
        pass


class LegacyItemAccess(object):
    """
    Provides expected passthru functionality for classes that still use
    self.data as the primary data structure for all parsed information.  Use
    this as a mixin on mappers that expect these methods to be present as they
    were previously.
    """

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def get(self, item, default=None):
        return self.data.get(item, default)


class LogFileMeta(type):
    def __new__(cls, name, parents, dct):
        dct["scanners"] = []
        return super(LogFileMeta, cls).__new__(cls, name, parents, dct)


class LogFileOutput(Mapper):

    __metaclass__ = LogFileMeta

    def parse_content(self, content):
        self.lines = list(content)
        for scanner in self.scanners:
            scanner(self)

    def __contains__(self, s):
        return any(s in l for l in self.lines)

    def get(self, s):
        return [line for line in self.lines if s in line]

    @classmethod
    def scan(cls, result_key, func):
        """
        Define computed fields based on a string to "grep for".  This is
        preferred to utilizing raw log lines in plugins because computed fields
        will be serialized, whereas raw log lines will not.
        """
        def scanner(self):
            result = func(self)
            setattr(self, result_key, result)
        cls.scanners.append(scanner)

    @classmethod
    def token_scan(cls, result_key, token):
        def _scan(self):
            return token in self
        cls.scan(result_key, _scan)

    @classmethod
    def keep_scan(cls, result_key, token):
        def _scan(self):
            return self.get(token)
        cls.scan(result_key, _scan)


class IniConfigFile(Mapper):
    """
        A class specifically for reading configuration files in 'ini' format:

        [section 1]
        key = value
        ; comment
        # comment
        [section 2]
        key with spaces = value string
    """

    def __init__(self, data, path=None, multikeys=[]):
        """
            Read the INI file and parse it now.

            Normally, if a key occurs later in the same section its value will
            replace the earlier value.  However, if this key is listed in the
            'multikeys' list this will cause these values to be appended to a
            list.  If multikeys is set to '*', all keys will do this.
        """
        #print "Got to INI file init: data:", data.content, "path:", path
        self.lines = data.content

        ini_data = {}
        section_dict = {}
        for line in data.content:
            #print "INI file: line =", line
            line = line.strip()
            if line.startswith("#") or line.startswith(';') or line == "":
                continue
            if line.startswith("["):
                # new section beginning
                section_dict = {}
                ini_data[line[1:].split(']',1)[0]] = section_dict
            elif '=' in line:
                key, value = [s.strip() for s in line.split("=", 1)]
                if key in section_dict and (
                 key in multikeys or multikeys == '*'):
                    # If we already have this key, and we want to keep
                    # multiple values for this key, append or listify it.
                    if isinstance(section_dict[key], list):
                        section_dict[key].append(value)
                    else:
                        section_dict[key] = [section_dict[key], value]
                else:
                    # Otherwise overwrite the previous value
                    section_dict[key] = value
        self.data = ini_data

        super(Mapper, self).__init__()

    def get(self, section):
        """
            Look up the section by name, return the entire dict
            (Should we throw a KeyError instead of returning None?)
        """
        if section not in self.data:
            return None
        return self.data[section]

    def __contains__(self, section):
        """
            Does the INI file contain this *section*?
        """
        return section in self.data

    def get_key(self, section, key):
        """
            Look up the given key in the given section, return the value
            or None if the section or key were not found.
            (Should we throw a KeyError instead of returning None?)
        """
        if section not in self.data:
            return None
        if key not in self.data[section]:
            return None
        return self.data[section][key]

    def __repr__(self):
        return "INI file - sections:[" + ', '.join(self.data.keys()) + "]"

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

if __name__ == "__main__":
    main()
