import argparse
import logging
import os
import re
import sys
from collections import defaultdict
from falafel.core import marshalling
import io
from ConfigParser import RawConfigParser

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
    log.debug("looking for files that match: [%s] in [%s]",
              pattern, plugin_dir)
    for root, dirs, files in os.walk(plugin_dir):
        if os.path.exists(os.path.join(root, "__init__.py")):
            for file_ in filter(name_filter, files):
                plugin_name, dot, suffix = file_.rpartition(".")
                if dot == "." and suffix == "py":
                    if get_importable_path(root):
                        yield "%s.%s" % (
                            get_importable_path(root), plugin_name)
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
    prefixes = [os.path.commonprefix([path, el]) for el in dirs
                if path.startswith(el)]
    longest = max(prefixes, key=len)
    if longest:
        return path.replace(longest, '').lstrip('/').replace('/', '.')
    else:
        raise Exception(
            "%s cannot be imported due to an insufficient sys.path" % path)


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
        self.file_name = os.path.basename(context.path) \
            if context.path is not None else None
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

        Note that we only pass through a few of the methods of RawConfigParser
        because we don't want people to write config files!  If there's a way
        to do this with multiple inheritance, patches are welcome :-)
    """

    def parse_content(self, content):
        config = RawConfigParser()
        fp = io.BytesIO("\n".join(content))
        config.readfp(fp, filename=self.file_name)
        self.data = config

    def sections(self):
        return self.data.sections()

    def items(self, section):
        return {k: v for (k, v) in self.data.items(section)}

    def get(self, section, key):
        return self.data.get(section, key)

    def getint(self, section, key):
        return self.data.getint(section, key)

    def getfloat(self, section, key):
        return self.data.getfloat(section, key)

    def getboolean(self, section, key):
        return self.data.getboolean(section, key)

    def has_option(self, section, key):
        return self.data.has_option(section, key)

    def __contains__(self, section):
        """
            Does the INI file contain this *section*?
        """
        return section in self.data.sections()

    def __repr__(self):
        return "INI file '{filename}' - sections:{sections}".\
            format(filename=self.file_name,
                   sections=self.data.sections())


class FileListing(Mapper):
    """
        Reads a series of concatenated directory listings and turns them into
        a dictionary of entities by name.  Stores all the information for
        each directory entry.  Also provides a number of other conveniences,
        such as:
         * a (name only) list of files and subdirectories for each directory
Examples:
dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
brw-rw----.  1 0 6 253,  10 Aug  4 16:56 dm-10
crw-------.  1 0 0 10,  236 Jul 25 10:00 control
    """

    # I know I'm missing some types in the 'type' subexpression...
    perms_regex = r'^(?P<type>[bcdlps-])' +\
        r'(?P<perms>[r-][w-][sSx-][r-][w-][sSx-][r-][w-][xsSt-]\S+)'
    links_regex = r'(?P<links>\d+)'
    owner_regex = r'(?P<owner>[a-zA-Z0-9_-]+)\s+(?P<group>[a-zA-Z0-9_-]+)'
    # In 'size' we also cope with major, minor format character devices
    # by just catching the \d+, and then splitting it off later.
    size_regex = r'(?P<size>(?:\d+,\s+)?\d+)(?P<frac>\.\d+)?' +\
        r'(?P<unit>[KMGTPEZY]?)'
    # Note that we don't try to determine nonexistent month, day > 31, hour
    # > 23, minute > 59 or improbable year here.
    # TODO: handle non-English formatted dates here.
    date_regex = r'(?P<date>\w{3}\s[ 0-9][0-9]\s(?:[ 0-9]\d:\d{2}|\s\d{4}))'
    name_regex = r'(?P<name>\S.*?)(?: -> (?P<link>\S+))?$'
    normal_regex = '\s+'.join((perms_regex, links_regex, owner_regex,
                              size_regex, date_regex, name_regex))
    normal_re = re.compile(normal_regex)
    normal_groups = ('type', 'perms', 'links', 'owner', 'group', 'size',
                     'date', 'name')
    # we also use the size regex when parsing a human-formatted total size,
    # so compile it separately
    size_re = re.compile(size_regex)

    context_regex = r'(?P<se_user>\w+_u):(?P<se_role>\w+_r):' +\
        r'(?P<se_type>\w+_t):(?P<se_mls>\S+)'
    selinux_regex = '\s+'.join((perms_regex, owner_regex, context_regex,
                               name_regex))
    selinux_re = re.compile(selinux_regex)
    selinux_groups = ('type', 'perms', 'owner', 'group', 'se_user', 'se_role',
                      'se_type', 'se_mls', 'name')

    # ls can give SI 'multiply by 1000' units with the --si option, but we
    # ignore that possibility here.
    size_of_unit = {'K': 1 << 10, 'M': 1 << 20, 'G': 1 << 30, 'T': 1 << 40,
                    'P': 1 << 50, 'E': 1 << 60, 'Y': 1 << 70, 'Z': 1 << 80}

    def __init__(self, context, selinux=False):
        """
            You can set the 'selinux' parameter to True to have this
            directory listing parsed as a 'ls -Z' directory listing.
        """
        self.selinux = selinux
        # Pick the right regex to use and save that as a property
        if selinux:
            self.file_regex = self.selinux_regex
            self.file_re = self.selinux_re
            self.file_groups = self.selinux_groups
        else:
            self.file_regex = self.normal_regex
            self.file_re = self.normal_re
            self.file_groups = self.normal_groups
        super(FileListing, self).__init__(context)

    def parse_size(self, match):
        """ Assumes a match from re.search on the size_regex """
        size = int(match.group('size'))
        if match.group('unit'):
            if match.group('frac'):
                # the frac group also captures the decimal point, so:
                size += float(match.group('frac'))
            size *= self.size_of_unit[match.group('unit')]
        return size

    def parse_file_match(self, this_dir, line):
        # Save all the raw directory entries, even if we can't parse them
        this_dir['raw_list'].append(line)
        match = self.file_re.search(line)
        if not match:
            # Can't do anything more with the line here
            return

        # Pull all the normal fields out of it
        this_file = {group: match.group(group) for group in self.file_groups}
        this_file['raw_entry'] = line
        typ = match.group('type')

        # There's a bunch of stuff that the SELinux listing doesn't contain:
        if not self.selinux:
            # Type conversions
            this_file['links'] = int(this_file['links'])
            # Is this a character or block device?  If so, it should
            # have a major, minor 'size':
            size = match.group('size')
            if typ in 'bc':
                # What should we do if we expect a major, minor size but
                # don't get one?
                if ',' in size:
                    major, minor = match.group('size').split(',')
                    this_file['major'] = int(major.strip())
                    this_file['minor'] = int(minor.strip())
                    # Remove 'size' entry since it's clearly invalid
                    del(this_file['size'])
            else:
                # What should we do if we get a comma here?
                if ',' not in size:
                    this_file['size'] = self.parse_size(match)

        # Is this a symlink?  If so, record what we link to.
        if match.group('link'):
            this_file['link'] = match.group('link')
        # Now add it to our various properties
        this_dir['entries'][this_file['name']] = this_file
        if typ in 'bc':
            this_dir['specials'].append(this_file['name'])
        if typ == 'd':
            this_dir['dirs'].append(this_file['name'])
        else:
            this_dir['files'].append(this_file['name'])

    def parse_content(self, content):
        listings = {}
        this_dir = {}
        for line in content:
            l = line.strip()
            if not l:
                continue
            if l.endswith(':'):
                # New structures for a new directory
                this_dir = {'entries': {}, 'files': [], 'dirs': [],
                            'specials': [], 'total': 0, 'raw_list': []}
                listings[l[:-1]] = this_dir
            elif l.startswith('total'):
                match = self.size_re.search(l[5:])
                if match:
                    this_dir['total'] = self.parse_size(match)
            else:
                self.parse_file_match(this_dir, l)

        self.listings = listings

    # Now some helpers to make some things easier:
    def __contains__(self, directory):
        return directory in self.listings

    def files_of(self, directory):
        return self.listings[directory]['files']

    def dirs_of(self, directory):
        return self.listings[directory]['dirs']

    def specials_of(self, directory):
        return self.listings[directory]['specials']

    def total_of(self, directory):
        return self.listings[directory]['total']

    def listing_of(self, directory):
        return self.listings[directory]['entries']

    def dir_contains(self, directory, name):
        return name in self.listings[directory]['entries']

    def dir_entry(self, directory, name):
        return self.listings[directory]['entries'][name]

    def raw_directory(self, directory):
        return self.listings[directory]['raw_list']


class ErrorCollector(object):
    errors = defaultdict(lambda: {
        "count": 0,
        "exception": None,
        "func": None
    })

    def __init__(self, verbose):
        self.verbose = verbose

    def reducer_error(self, func, e, local, shared):
        key = "".join([func.__module__, str(type(e)), str(e.message)])
        error = self.errors[key]
        error["count"] = error["count"] + 1
        error["exception"] = e
        error["tb"] = sys.exc_info()[2]
        error["func"] = func

    def has_errors(self):
        return len(self.errors) > 0

    def format_errors(self):
        for error in self.errors.values():
            e = error["exception"]
            func = error["func"]
            count = error["count"]
            ename = e.__class__.__name__
            yield "%d count(s) of [%s]: %s: %s" % \
                (count, func.__module__, ename, e.message)
            if self.verbose:
                import traceback
                traceback.print_exception(type(e), e, error["tb"])
                yield ""


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
    min_key_len = max([0] + [len(r["error_key"]) for h, f, r in results
                      if "error_key" in r])
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
        "Only run mappers.  Pipes mapper output to stdout.",
        "Print a traceback for each kind of error caught."
    ]
    p = argparse.ArgumentParser("insights-run")
    p.add_argument(
        "-p", "--pattern", dest="pattern", help=HELP[0])
    p.add_argument(
        "-t", "--tracebacks", dest="tracebacks", action="store_true",
        default=False, help=HELP[4])
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
        ec = ErrorCollector(args.tracebacks)
        results = list(reducer.run(mapper_results, ec.reducer_error))
        print_results(results, error_collector=ec)
    else:
        log.warning("Running mappers")
        cases, mapper_results = mapper.run(sys.stdin)
        log.warning("Running reducers")
        ec = ErrorCollector(args.tracebacks)
        results = list(reducer.run(mapper_results, ec.reducer_error))
        print_results(results, cases, ec)

if __name__ == "__main__":
    main()
