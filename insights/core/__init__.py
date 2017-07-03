import datetime
import io
import logging
import os
import pkgutil
import re
import shlex
import sys
import yaml
from ConfigParser import RawConfigParser

from insights.parsers import ParseException

DEFAULT_PATTERN = r'.*py$'
DEFAULT_PLUGIN_MODULE = "insights.plugins"
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
            module = loader.find_module(name)
            try:
                filename = module.filename
            except AttributeError:
                # filename attribute is not populated for modules from eggs
                # create a virtual filename to feed to the filter
                filename = "%s.py" % name.replace('.', '/')

            if name_filter(filename):
                yield name


class Parser(object):
    """
    Base class designed to be subclassed by parsers.

    The framework will construct your object with a `Context` that will
    provide *at least* the content as an interable of lines and the path
    that the content was retrieved from.

    Facts should be exposed as instance members where applicable. For
    example::

        self.fact = "123"

    Examples:
        >>> class MyParser(Parser):
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
        >>> my_parser = MyParser(context_wrap(content, path='/etc/path_to_content/content.conf'))
        >>> my_parser.facts
        ['fact=fact 1', 'fact=fact 2', 'fact=fact 3']
        >>> my_parser.file_path
        '/etc/path_to_content/content.conf'
        >>> my_parser.file_name
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


class SysconfigOptions(Parser):
    """
    A parser to handle the standard 'keyword=value' format of files in the
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
            if not line or line.startswith('#'):
                continue

            try:
                words = shlex.split(line)
            except ValueError:
                # Handle foo=bar # unpaired ' or " here
                line, comment = line.split(' #', 1)
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

    def __getitem__(self, option):
        """
        Retrieves an item from the underlying data dictionary.
        """
        return self.data[option]

    def __contains__(self, option):
        """
        Does the underlying dictionary contain this option?
        """
        return option in self.data

    def keys(self):
        """
        Return the list of keys (in no order) in the underlying dictionary.
        """
        return self.data.keys()

    def get(self, item, default=None):
        """Returns value of key ``item`` in self.data or ``default``
        if key is not present.

        Parameters:
            item (str): Key to get from ``self.data``.
            default (str): Default value to return if key is not present.

        Returns:
            (str): String value of the stored item, or the default if not found.
        """
        return self.data.get(item, default)


class LegacyItemAccess(object):
    """
    Mixin class to provide legacy access to ``self.data`` attribute.

    Provides expected passthru functionality for classes that still use
    ``self.data`` as the primary data structure for all parsed information.  Use
    this as a mixin on parsers that expect these methods to be present as they
    were previously.

    Examples:
        >>> class MyParser(LegacyItemAccess, Parser):
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
        >>> my_parser = MyParser(context_wrap(content, path='/etc/path_to_content/content.conf'))
        >>> my_parser.data
        {'fact1': 'fact 1', 'fact2': 'fact 2', 'fact3': 'fact 3'}
        >>> my_parser.file_path
        '/etc/path_to_content/content.conf'
        >>> my_parser.file_name
        'content.conf'
        >>> my_parser['fact1']
        'fact 1'
        >>> 'fact2' in my_parser
        True
        >>> my_parser.get('fact3', default='no fact')
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

        Returns:
            (str): String value of the stored item, or the default if not found.
        """
        return self.data.get(item, default)


class YAMLParser(Parser, LegacyItemAccess):
    """
    A parser class that reads YAML files.  Base your own parser on this.
    """
    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))


class ScanMeta(type):
    def __new__(cls, name, parents, dct):
        dct["scanners"] = []
        dct["scanner_keys"] = set()
        return super(ScanMeta, cls).__new__(cls, name, parents, dct)


class Scannable(Parser):

    __metaclass__ = ScanMeta

    @classmethod
    def _scan(cls, result_key, scanner):
        """
        Registers a `scanner` which is a function that will be called once per
        logical line in a document. A scanners job is to evaluate the content
        of the line and set a so-called `result_key` on the class to be
        retrieved later by a rule.
        """

        if result_key in cls.scanner_keys:
            raise ValueError("'%s' is already a registered scanner key" % result_key)

        cls.scanners.append(scanner)
        cls.scanner_keys.add(result_key)

    @classmethod
    def any(cls, result_key, func):
        """
        Sets the `result_key` to the output of `func` if `func` ever returns
        truthy
        """
        def scanner(self, obj):
            current_value = getattr(self, result_key, None)
            setattr(self, result_key, current_value or func(obj))

        cls._scan(result_key, scanner)

    @classmethod
    def collect(cls, result_key, func):
        """
        Sets the `result_key` to an iterable of objects for which `func(obj)`
        returns True
        """
        def scanner(self, obj):
            if not getattr(self, result_key, None):
                setattr(self, result_key, [])
            rv = func(obj)
            if rv:
                getattr(self, result_key).append(rv)

        cls._scan(result_key, scanner)

    def parse(self, content):
        """
        Default 'parsing' method. Subclasses should override this method with
        their own custom parsing as necessary.
        """
        for line in content:
            yield line

    def parse_content(self, content):
        for obj in self.parse(content):
            for scanner in self.scanners:
                scanner(self, obj)


class LogFileOutput(Parser):
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
    __metaclass__ = ScanMeta

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

    def get_after(self, timestamp, lines=None, time_format='%Y-%m-%d %H:%M:%S'):
        """
        Find all the (available) logs that are after the given time stamp.

        This method should be used by the subclass to provide an actual
        ``get_after()`` method which provides the standard time stamp format
        used by its particular log.  This method should only be used if the
        subclass does not present its own or the caller needs to override
        the default time format.

        If 'lines' is not supplied, then all lines are used.  Otherwise, the
        caller can provide a list of lines from a scanner or the ``get()``
        method.

        This method then finds all lines in that list which have a time stamp
        after the given timestamp.  Lines that do not contain a time stamp
        are considered to be part of the previous line and are therefore
        included if the last log line was included or excluded otherwise.

        This works by converting the time format into a regular expression
        which matches the time format in the string.  This is then searched
        for in each line in turn.  Only lines with a time stamp matching this
        expression will trigger the decision to include or exclude lines.
        Therefore, if the log for some reason does not contain a time stamp
        that matches this format, no lines will be returned.

        Lines can be either a single string or a dictionary.  String lines
        search for a time stamp in the entire line.  Dictionary lines look
        for a field named 'timestamp', which is (still) searched for a valid
        time format as above - lines without the 'timestamp' field are
        treated as continuation lines (see above).

        Note: Some logs - notably /var/log/messages - do not contain a year
        in the timestamp.  This detected by the absence of a '%y' or '%Y' in
        the time format.  If that year field is absent, the year is assumed
        to be the year in the given timestamp being sought.  Some attempt is
        made to handle logs with a rollover from December to January, by
        finding when the log's timestamp (with current year assumed) is over
        eleven months (specifically, 330 days) ahead of or behind the
        timestamp date and shifting that log date by 365 days so that it is
        more likely to be in the sought range.  This paragraph is sponsored
        by syslog.

        No attempt is made to order the lines by date.  This also means that
        lines can be out of order, as each timestamp is evaluated individually.

        Parameters:

            timestamp(datetime.datetime): lines before this time are ignored.
            lines(list): an optional list of lines from this parser to search.
            time_format(str): the ``strptime()`` string of the format of the
                dates in this log.

        Yields:
            (string/dict): the lines with timestamps after this date in the
            same format they were supplied.

        Raises:
            ParseException: If the format conversion string contains a
                format that we don't recognise.  In particular, no attempt is
                made to recognise or parse the time zone or other obscure
                values like day of year or week of year.
        """
        if lines is None:
            lines = self.lines

        logs_have_year = ('%Y' in time_format or '%y' in time_format)

        # Annoyingly, strptime insists that it get the whole time string and
        # nothing but the time string.  However, for most logs we only have a
        # string with the timestamp in it.  We can't just catch the ValueError
        # because at that point we do not actually have a valid datetime
        # object.  So we convert the time format string to a regex, use that
        # to find just the timestamp, and then use strptime on that.  Thanks,
        # Python.  All these need to cope with different languages and
        # character sets.  Note that we don't include time zone or other
        # outputs (e.g. day-of-year) that don't usually occur in time stamps.
        format_conversion_for = {
            'a': r'\w{3}', 'A': r'\w+',  # Week day name
            'w': r'[0123456]',  # Week day number
            'd': r'([0 ][123456789]|[12]\d|3[01])',  # Day of month
            'b': r'\w{3}', 'B': r'\w+',  # Month name
            'm': r'(0\d|1[012])',  # Month number
            'y': r'\d{2}', 'Y': r'\d{4}',  # Year
            'H': r'([01]\d|2[0123])',  # Hour - 24 hour format
            'I': r'(0\d|1[012])',  # Hour - 12 hour format
            'p': r'\w[2}',  # AM / PM
            'M': r'([012345]\d)',  # Minutes
            'S': r'([012345]\d|60)',  # Seconds, including leap second
            'f': r'\d{6}',  # Microseconds
        }

        # Construct the regex from the time string
        timefmt_re = re.compile(r'%(\w)')

        def replacer(match):
            if match.group(1) in format_conversion_for:
                return format_conversion_for[match.group(1)]
            else:
                raise ParseException(
                    "_get_after does not understand strptime format '{c}'".format(
                        c=match.group(0)
                    )
                )

        # Please do not attempt to be tricky and put a regular expression
        # inside your time format, as we are going to also use it in
        # strptime too and that may not work out so well.
        time_re = re.compile('(' + timefmt_re.sub(replacer, time_format) + ')')

        # Most logs will appear in string format, but some logs (e.g.
        # Messages) are available in list-of-dicts format.  So we choose one
        # of two 'date_compare' functions.  HOWEVER: we still have to check
        # the string found for a valid date, because log parsing often fails.
        # Because of generators, we check this per line

        # Now try to find the time stamp in each log line and add lines to
        # our output if they are currently being included in the log.
        eleven_months = datetime.timedelta(days=330)
        including_lines = False
        for line in lines:
            # Evaluate here because of generators
            if type(line) == str:
                s = line
            elif type(line) == dict:
                s = line.get('timestamp', '')
            else:
                raise ValueError("Cannot search objects of type {t} for timestamps")

            match = time_re.search(s)
            if match:
                logstamp = datetime.datetime.strptime(match.group(0), time_format)
                if not logs_have_year:
                    # Substitute timestamp year for logstamp year
                    logstamp = logstamp.replace(year=timestamp.year)
                    if logstamp - timestamp > eleven_months:
                        # If timestamp in January and log in December, move
                        # log to previous year
                        logstamp = logstamp.replace(year=timestamp.year - 1)
                    elif timestamp - logstamp > eleven_months:
                        # If timestamp in December and log in January, move
                        # log to next year
                        logstamp = logstamp.replace(year=timestamp.year + 1)
                if logstamp >= timestamp:
                    # Later - include
                    including_lines = True
                    yield line
                else:
                    # Earlier - start excluding
                    including_lines = False
            else:
                # If we're including lines, add this continuation line
                if including_lines:
                    yield line


class IniConfigFile(Parser):
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


class FileListing(Parser):
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
    # Modify the last '\S+' to '\S*' to match where there is no '.' at the end
    perms_regex = r'^(?P<type>[bcdlps-])' +\
        r'(?P<perms>[r-][w-][sSx-][r-][w-][sSx-][r-][w-][xsSt-]([.+-])?)'
    links_regex = r'(?P<links>\d+)'
    owner_regex = r'(?P<owner>[a-zA-Z0-9_-]+)\s+(?P<group>[a-zA-Z0-9_-]+)'
    # In 'size' we also cope with major, minor format character devices
    # by just catching the \d+, and then splitting it off later.
    size_regex = r'(?P<size>(?:\d+,\s+)?\d+)'
    # Note that we don't try to determine nonexistent month, day > 31, hour
    # > 23, minute > 59 or improbable year here.
    # TODO: handle non-English formatted dates here.
    date_regex = r'(?P<date>\w{3}\s[ 0-9][0-9]\s(?:[012]\d:\d{2}|\s\d{4}))'
    name_regex = r'(?P<name>[^/ ][^/]*?)(?: -> (?P<link>\S.*))?$'
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
        this_file['dir'] = this_dir['name']
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
        file_name = this_file['name']
        this_dir['entries'][file_name] = this_file
        if typ in 'bc':
            this_dir['specials'].append(file_name)
        if typ == 'd':
            this_dir['dirs'].append(file_name)
        else:
            this_dir['files'].append(file_name)

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
            if l.startswith('/') and l.endswith(':'):
                # New structures for a new directory
                name = l[:-1]
                this_dir = {'entries': {}, 'files': [], 'dirs': [],
                            'specials': [], 'total': 0, 'raw_list': [],
                            'name': name}
                listings[name] = this_dir
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

    def path_entry(self, path):
        """
        The parsed data given a path, which is separated into its directory
        and entry name.
        """
        if path[0] != '/':
            return None
        path_parts = path.split('/')
        # Note that here the first element will be '' because it's before the
        # first separator.  That's OK, the join puts it back together.
        directory = '/'.join(path_parts[:-1])
        name = path_parts[-1]
        if directory not in self.listings:
            return None
        if name not in self.listings[directory]['entries']:
            return None
        return self.listings[directory]['entries'][name]

    def raw_directory(self, directory):
        """
        The list of raw lines from the directory, as is.
        """
        return self.listings[directory]['raw_list']


class AttributeDict(dict):
    """
    Class to convert the access to each item in a dict as attribute.

    Examples:
        >>> data = {
        ... "fact1":"fact 1"
        ... "fact2":"fact 2"
        ... "fact3":"fact 3"
        ... }
        >>> d_obj = AttributeDict(data)
        {'fact1': 'fact 1', 'fact2': 'fact 2', 'fact3': 'fact 3'}
        >>> d_obj['fact1']
        'fact 1'
        >>> d_obj.get('fact1')
        'fact 1'
        >>> d_obj.fact1
        'fact 1'
        >>> 'fact2' in d_obj
        True
        >>> d_obj.get('fact3', default='no fact')
        'fact 3'
        >>> d_obj.get('fact4', default='no fact')
        'no fact'
    """

    def __init__(self, *args, **kwargs):
        super(AttributeDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __iter__(self):
        for k, v in self.__dict__.iteritems():
            yield k, v
