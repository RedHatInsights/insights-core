import argparse
import io
import logging
import os
import pkgutil
import re
import shlex
import sys
from ConfigParser import RawConfigParser
from collections import defaultdict

from falafel.core import marshalling

DEFAULT_PATTERN = r'.*py$'
DEFAULT_PLUGIN_MODULE = "falafel.plugins"
log = logging.getLogger(__name__)


def load_package(package_name, pattern=None, loaded_map=set()):
    loaded = []

    if package_name in loaded_map:
        return

    __import__(package_name, globals(), locals(), [], -1)

    for module_name in get_module_names(package_name, pattern):
        m = __import__(module_name, globals(), locals(), [package_name], -1)
        loaded.append(m)
        log.debug("loaded %s", module_name)

    loaded_map.add(package_name)
    log.info("Loaded %d modules", len(loaded))
    return loaded


def get_module_names(package_name, pattern=None):
    matcher = re.compile('.*' + pattern + '.*' if pattern else DEFAULT_PATTERN)

    def name_filter(name):
        if "__init__" not in name and "__main__" not in name:
            if matcher.match(name):
                return True
        return False

    search_paths = (
        package_name.replace('.', '/'),
        os.path.dirname(os.path.realpath(sys.modules[package_name].__file__))
    )
    log.debug("looking for files that match: [%s] in [%s]", pattern, search_paths)
    for loader, name, ispkg in pkgutil.walk_packages(search_paths, package_name + '.'):
        if not ispkg:
            # absolute path of the module
            filename = loader.find_module(name).filename
            if name_filter(filename):
                yield name


class Mapper(object):
    """
    Base class designed to be subclassed by mappers.

    The framework will construct your object with a `Context` that will
    provide *at least* the content as an interable of lines and the path
    that the content was retrieved from.

    Facts should be exposed as instance members where applicable. For
    example::

        self.fact = "123"

    Examples:
        >>> class MyMapper(Mapper):
        ...     def parse_content(self, content):
        ...         self.facts = []
        ...         for line in content:
        ...             if 'fact' in line:
        ...                 self.facts.append(line)
        >>> content = '''
        ... # Comment line
        ... fact=fact 1
        ... fact=fact 2
        ... fact=fact 3
        ... '''.strip()
        >>> my_mapper = MyMapper(context_wrap(content, path='/etc/path_to_content/content.conf'))
        >>> my_mapper.facts
        ['fact=fact 1', 'fact=fact 2', 'fact=fact 3']
        >>> my_mapper.file_path
        '/etc/path_to_content/content.conf'
        >>> my_mapper.file_name
        'content.conf'
    """

    def __init__(self, context):
        self.file_path = context.path
        """str: Full context path of the input file."""
        self.file_name = os.path.basename(context.path) \
            if context.path is not None else None
        """str: Filename portion of the input file."""
        if hasattr(context, "last_client_run"):
            self.last_client_run = context.last_client_run
        else:
            self.last_client_run = None
        self.parse_content(context.content)

    def parse_content(self, content):
        """This method must be implemented by classes based on this class."""
        pass


class SysconfigOptions(Mapper):
    """
    A mapper to handle the standard 'keyword=value' format of files in the
    ``/etc/sysconfig`` directory.  These are provided in the standard 'data'
    dictionary.

    Examples:

        >>> ntpconf = shared[NtpConf]
        >>> 'OPTIONS' in ntpconf.data
        True
        >>> 'NOT_SET' in ntpconf.data
        False
        >>> 'COMMENTED_OUT' in ntpconf.data
        False
        >>> ntpconf.data['OPTIONS']
        '-x -g'

    For common variables such as OPTIONS, it is recommended to set a specific
    property in the subclass that fetches this option with a fallback to a
    default value.

    Example subclass::

        class DirsrvSysconfig(SysconfigOptions):

            @property
            def options(self):
                return self.data.get('OPTIONS', '')
    """

    def parse_content(self, content):
        result = {}
        unparsed_lines = []

        # Do not use get_active_lines, it strips comments within quotes
        for line in content:
            if not line:
                continue
            words = shlex.split(line)
            # Either only one thing or line or rest starts with comment
            # but either way we need to have an equals in the first word.
            if (len(words) == 1 or (len(words) > 1 and words[1][0] == '#')) \
                    and '=' in words[0]:
                key, value = words[0].split('=', 1)
                result[key] = value
            # Only store lines if they aren't comments or blank
            elif len(words) > 0 and words[0][0] != '#':
                unparsed_lines.append(line)
        self.data = result
        self.unparsed_lines = unparsed_lines


class LegacyItemAccess(object):
    """
    Mixin class to provide legacy access to ``self.data`` attribute.

    Provides expected passthru functionality for classes that still use
    ``self.data`` as the primary data structure for all parsed information.  Use
    this as a mixin on mappers that expect these methods to be present as they
    were previously.

    Examples:
        >>> class MyMapper(LegacyItemAccess, Mapper):
        ...     def parse_content(self, content):
        ...         self.data = {}
        ...         for line in content:
        ...             if 'fact' in line:
        ...                 k, v = line.split('=')
        ...                 self.data[k.strip()] = v.strip()
        >>> content = '''
        ... # Comment line
        ... fact1=fact 1
        ... fact2=fact 2
        ... fact3=fact 3
        ... '''.strip()
        >>> my_mapper = MyMapper(context_wrap(content, path='/etc/path_to_content/content.conf'))
        >>> my_mapper.data
        {'fact1': 'fact 1', 'fact2': 'fact 2', 'fact3': 'fact 3'}
        >>> my_mapper.file_path
        '/etc/path_to_content/content.conf'
        >>> my_mapper.file_name
        'content.conf'
        >>> my_mapper['fact1']
        'fact 1'
        >>> 'fact2' in my_mapper
        True
        >>> my_mapper.get('fact3', default='no fact')
        'fact 3'
    """

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data

    def get(self, item, default=None):
        """Returns value of key ``item`` in self.data or ``default``
        if key is not present.

        Parameters:
            item: Key to get from ``self.data``.
            default: Default value to return if key is not present.
        """
        return self.data.get(item, default)


class ScanMeta(type):
    def __new__(cls, name, parents, dct):
        dct["scanners"] = []
        dct["scanner_keys"] = set()
        return super(ScanMeta, cls).__new__(cls, name, parents, dct)


class Scannable(Mapper):

    __metaclass__ = ScanMeta

    @classmethod
    def _scan(cls, result_key, scanner):
        """
        Define computed fields based on a string to "grep for".  This is
        preferred to utilizing raw log lines in plugins because computed fields
        will be serialized, whereas raw log lines will not.
        """

        if result_key in cls.scanner_keys:
            raise ValueError("'%s' is already a registered scanner key" % result_key)

        cls.scanners.append(scanner)
        cls.scanner_keys.add(result_key)

    @classmethod
    def scan_any(cls, result_key, func):
        def scanner(self, obj):
            current_value = getattr(self, result_key, None)
            setattr(self, result_key, current_value and func(obj))

        Scannable._scan(result_key, scanner)

    @classmethod
    def scan_latch(cls, result_key, func):
        def scanner(self, obj):
            current_value = getattr(self, result_key, None)
            setattr(self, result_key, current_value or func(obj))

        Scannable._scan(result_key, scanner)


class LogFileMeta(type):
    def __new__(cls, name, parents, dct):
        dct["scanners"] = []
        dct["scanner_keys"] = set()
        return super(LogFileMeta, cls).__new__(cls, name, parents, dct)


class LogFileOutput(Mapper):
    """Class for parsing log file content.

    Log file content is stored in raw format in the ``lines`` attribute.

    Attributes:
        lines (list): List of the lines from the log file content.

    Examples:
        >>> class MyLogger(LogFileOutput):
        ...     pass
        >>> contents = '''
        Log file line one
        Log file line two
        Log file line three
        '''.strip()
        >>> my_logger = MyLogger(context_wrap(contents, path='/var/log/mylog'))
        >>> my_logger.file_path
        '/var/log/mylog'
        >>> my_logger.file_name
        'mylog'
        >>> my_logger.lines.get('two')
        ['Log file line two']
        >>> 'three' in my_logger
        True
        >>> my_logger.lines[0]
        'Log file line one'
    """
    __metaclass__ = LogFileMeta

    def parse_content(self, content):
        """
        Use all the defined scanners to search the log file, setting the
        properties defined in the scanner.
        """
        self.lines = list(content)
        for scanner in self.scanners:
            scanner(self)

    def __contains__(self, s):
        """
        Returns true if any line contains the given text string.
        """
        return any(s in l for l in self.lines)

    def get(self, s):
        """list: Returns lis of lines containing string ``s``."""
        return [line for line in self.lines if s in line]

    @classmethod
    def scan(cls, result_key, func):
        """
        Define computed fields based on a string to "grep for".  This is
        preferred to utilizing raw log lines in plugins because computed fields
        will be serialized, whereas raw log lines will not.
        """

        if result_key in cls.scanner_keys:
            raise ValueError("'%s' is already a registered scanner key" % result_key)

        def scanner(self):
            result = func(self)
            setattr(self, result_key, result)

        cls.scanners.append(scanner)
        cls.scanner_keys.add(result_key)

    @classmethod
    def token_scan(cls, result_key, token):
        """
        Define a property that is set to true if the given token is found in
        the log file.  Uses the __contains__ method of the log file.
        """
        def _scan(self):
            return token in self

        cls.scan(result_key, _scan)

    @classmethod
    def keep_scan(cls, result_key, token):
        """
        Define a property that is set to the list of lines that contain the
        given token.  Uses the get method of the log file.
        """
        def _scan(self):
            return self.get(token)

        cls.scan(result_key, _scan)


class IniConfigFile(Mapper):
    """
    A class specifically for reading configuration files in 'ini' format.

    The input file format supported by this class is::

           [section 1]
           key = value
           ; comment
           # comment
           [section 2]
           key with spaces = value string
           [section 3]
           # Must implement parse_content in child class
           # and pass allow_no_value=True to parent class
           # to enable keys with no values
           key_with_no_value

    References:
        See Python ``RawConfigParser`` documentation for more information
        https://docs.python.org/2/library/configparser.html#rawconfigparser-objects

    Examples:
        >>> class MyConfig(IniConfigFile):
        ...     pass
        >>> content = '''
        ... [defaults]
        ... admin_token = ADMIN
        ... [program opts]
        ... memsize = 1024
        ... delay = 1.5
        ... [logging]
        ... log = true
        ... logging level = verbose
        ... '''.split()
        >>> my_config = MyConfig(context_wrap(content, path='/etc/myconfig.conf'))
        >>> 'program opts' in my_config
        True
        >>> my_config.sections()
        ['program opts', 'logging']
        >>> my_config.defaults()
        {'admin_token': 'ADMIN'}
        >>> my_config.items('program opts')
        {'memsize': 1024, 'delay': 1.5}
        >>> my_config.get('logging', 'logging level')
        'verbose'
        >>> my_config.getint('program opts', 'memsize')
        1024
        >>> my_config.getfloat('program opts', 'delay')
        1.5
        >>> my_config.getboolean('logging', 'log')
        True
        >>> my_config.has_option('logging', 'log')
        True
    """

    def parse_content(self, content, allow_no_value=False):
        """Parses content of the config file.

        In child class overload and call super to set flag
        ``allow_no_values`` and allow keys with no value in
        config file::

            def parse_content(self, content):
                super(YourClass, self).parse_content(content,
                                                     allow_no_values=True)
        """
        config = RawConfigParser(allow_no_value=allow_no_value)
        fp = io.BytesIO("\n".join(content))
        config.readfp(fp, filename=self.file_name)
        self.data = config

    def sections(self):
        """list: Return a list of section names."""
        return self.data.sections()

    def defaults(self):
        """list: Return a dict of key/value pairs in the ``[default]`` section."""
        return self.data.defaults()

    def items(self, section):
        """dict: Return a dictionary of key/value pairs for ``section``."""
        return {k: v for (k, v) in self.data.items(section)}

    def get(self, section, key):
        """value: Get value for ``section`` and ``key``."""
        return self.data.get(section, key)

    def getint(self, section, key):
        """int: Get int value for ``section`` and ``key``."""
        return self.data.getint(section, key)

    def getfloat(self, section, key):
        """float: Get float value for ``section`` and ``key``."""
        return self.data.getfloat(section, key)

    def getboolean(self, section, key):
        """boolean: Get boolean value for ``section`` and ``key``."""
        return self.data.getboolean(section, key)

    def has_option(self, section, key):
        """boolean: Returns ``True`` of ``section`` is present and has option
        ``key``."""
        return self.data.has_option(section, key)

    def __contains__(self, section):
        return section in self.data.sections()

    def __repr__(self):
        return "INI file '{filename}' - sections:{sections}".\
            format(filename=self.file_name,
                   sections=self.data.sections())


class FileListing(Mapper):
    """
    Reads a series of concatenated directory listings and turns them into
    a dictionary of entities by name.  Stores all the information for
    each directory entry for every entry that can be parsed, containing:

    * type (one of [bcdlps-])
    * permission string including ACL character
    * number of links
    * owner and group (as given in the listing)
    * size, or major and minor number for block and character devices
    * date (in the format given in the listing)
    * name
    * name of linked file, if a symlink

    In addition, the raw line is always stored, even if the line doesn't look
    like a directory entry.

    Also provides a number of other conveniences, such as:

    * lists of regular and special files and subdirectory names for each
      directory, in the order found in the listing
    * total blocks allocated to all the entities in this directory

    Parses SELinux directory listings if the 'selinux' option is True.
    SELinux directory listings contain:

    * the type of file
    * the permissions block
    * the owner and group as given in the directory listing
    * the SELinux user, role, type and MLS
    * the name, and link destination if it's a symlink

    Sample input data looks like this:

        | /example_dir:
        | total 20
        | dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
        | -rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
        | lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
        | brw-rw----.  1 0 6 253,  10 Aug  4 16:56 dm-10
        | crw-------.  1 0 0 10,  236 Jul 25 10:00 control

    Examples:
        >>> '/example_dir' in shared[FileListing]
        True
        >>> shared[FileListing].dir_contains('/example_dir', 'menu.lst')
        True
        >>> dir = shared[FileListing].listing_of('/example_dir')
        >>> dir['.']['type']
        'd'
        >>> dir['config-3.10.0-229.14.q.el7.x86_64']['size']
        123891
        >>> dir['dm-10']['major']
        253
        >>> dir['menu.lst']['link']
        './grub.conf'
    """

    # I know I'm missing some types in the 'type' subexpression...
    perms_regex = r'^(?P<type>[bcdlps-])' +\
        r'(?P<perms>[r-][w-][sSx-][r-][w-][sSx-][r-][w-][xsSt-]\S+)'
    links_regex = r'(?P<links>\d+)'
    owner_regex = r'(?P<owner>[a-zA-Z0-9_-]+)\s+(?P<group>[a-zA-Z0-9_-]+)'
    # In 'size' we also cope with major, minor format character devices
    # by just catching the \d+, and then splitting it off later.
    size_regex = r'(?P<size>(?:\d+,\s+)?\d+)'
    # Note that we don't try to determine nonexistent month, day > 31, hour
    # > 23, minute > 59 or improbable year here.
    # TODO: handle non-English formatted dates here.
    date_regex = r'(?P<date>\w{3}\s[ 0-9][0-9]\s(?:[012]\d:\d{2}|\s\d{4}))'
    name_regex = r'(?P<name>\S.*?)(?: -> (?P<link>\S+))?$'
    normal_regex = '\s+'.join((perms_regex, links_regex, owner_regex,
                              size_regex, date_regex, name_regex))
    normal_re = re.compile(normal_regex)

    context_regex = r'(?P<se_user>\w+_u):(?P<se_role>\w+_r):' +\
        r'(?P<se_type>\w+_t):(?P<se_mls>\S+)'
    selinux_regex = '\s+'.join((perms_regex, owner_regex, context_regex,
                               name_regex))
    selinux_re = re.compile(selinux_regex)

    def __init__(self, context, selinux=False):
        """
            You can set the 'selinux' parameter to True to have this
            directory listing parsed as a 'ls -Z' directory listing.
        """
        self.selinux = selinux
        # Pick the right regex to use and save that as a property
        if selinux:
            self.file_re = self.selinux_re
        else:
            self.file_re = self.normal_re
        super(FileListing, self).__init__(context)

    def parse_file_match(self, this_dir, line):
        # Save all the raw directory entries, even if we can't parse them
        this_dir['raw_list'].append(line)
        match = self.file_re.search(line)
        if not match:
            # Can't do anything more with the line here
            return

        # Get the fields from the regex
        this_file = match.groupdict()
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
                    # Remove other 'size' entries
                    del(this_file['size'])
            else:
                # What should we do if we get a comma here?
                if ',' not in size:
                    this_file['size'] = int(match.group('size'))

        # If this is not a symlink, remove the link key
        if not this_file['link']:
            del this_file['link']
        # Now add it to our various properties
        this_dir['entries'][this_file['name']] = this_file
        if typ in 'bc':
            this_dir['specials'].append(this_file['name'])
        if typ == 'd':
            this_dir['dirs'].append(this_file['name'])
        else:
            this_dir['files'].append(this_file['name'])

    def parse_content(self, content):
        """
        Called automatically to process the directory listing(s) contained in
        the content.
        """
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
            elif l.startswith('total') and l[6:].isdigit():
                this_dir['total'] = int(l[6:])
            elif not this_dir:
                # This state can happen if processing an archive that filtered
                # a file listing due to an old spec definition.
                # Let's just skip these lines.
                continue
            else:
                self.parse_file_match(this_dir, l)

        self.listings = listings

    # Now some helpers to make some things easier:
    def __contains__(self, directory):
        """
        Does the given directory appear in this set of directory listings?
        """
        return directory in self.listings

    def files_of(self, directory):
        """
        The list of non-special files (i.e. not block or character files)
        in the given directory.
        """
        return self.listings[directory]['files']

    def dirs_of(self, directory):
        """
        The list of subdirectories in the given directory.
        """
        return self.listings[directory]['dirs']

    def specials_of(self, directory):
        """
        The list of block and character special files in the given directory.
        """
        return self.listings[directory]['specials']

    def total_of(self, directory):
        """
        The total blocks of storage consumed by entries in this directory.
        """
        return self.listings[directory]['total']

    def listing_of(self, directory):
        """
        The listing of this directory, in a dictionary by entry name.  All
        entries contain the original line as is in the 'raw_entry' key.
        Entries that can be parsed then have fields as described in the class
        description above.
        """
        return self.listings[directory]['entries']

    def dir_contains(self, directory, name):
        """
        Does this directory contain this entry name?
        """
        return name in self.listings[directory]['entries']

    def dir_entry(self, directory, name):
        """
        The parsed data for the given entry name in the given directory.
        """
        return self.listings[directory]['entries'][name]

    def raw_directory(self, directory):
        """
        The list of raw lines from the directory, as is.
        """
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
        # like result_count, filter result with "error_key"
        if "error_key" in r:
            case = cases.get(host) if cases else None
            print_result(r, case=case, min_key_len=min_key_len)
    print "Result count:", result_count
    if error_collector and error_collector.has_errors():
        print "\n===== ERRORS ====="
        for error_str in error_collector.format_errors():
            print error_str


def main():
    from falafel.core import mapper, reducer
    p = argparse.ArgumentParser("insights-run")
    p.add_argument(
        "-p", "--pattern", dest="pattern",
        help="Pattern used to filter out plugins for execution."
    )
    p.add_argument(
        "-t", "--tracebacks", dest="tracebacks", action="store_true",
        default=False,
        help="Print a traceback for each kind of error caught."
    )
    p.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true",
        default=False,
        help="Verbose console logging (n.b. it's *very* verbose)."
    )
    p.add_argument(
        "-r", "--reduce-only", dest="reduce_only",
        action="store_true", default=False,
        help="Only run reducers.  Expect mapper output from stdin."
    )
    p.add_argument(
        "-m", "--map-only", dest="map_only", action="store_true",
        default=False,
        help="Only run mappers.  Pipes mapper output to stdout."
    )
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
        # print mapper.serialize(mapper_results)
        # as there is no serialize method, print the result directly
        print mapper_results
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
