import collections
import inspect
import logging
import functools
import platform
import os
import warnings
import datetime


TMP_DIR = os.path.join("/tmp", "insights-web")
logger = logging.getLogger(__name__)

TRUTH = {
    "true": True,
    "false": False,
    "yes": True,
    "no": False,
    "1": True,
    "0": False
}


def parse_bool(s, default=False):
    """
    Return the boolean value of an English string or default if it can't be
    determined.
    """
    if s is None:
        return default
    return TRUTH.get(s.lower(), default)


# python2 doesn't have a utc tzinfo by default
# see https://docs.python.org/2/library/datetime.html#tzinfo-objects
try:
    utc = datetime.timezone.utc
except:
    class UTC(datetime.tzinfo):
        """
        A tzinfo class for UTC.
        """
        ZERO = datetime.timedelta(0)

        def utcoffset(self, dt):
            return self.ZERO

        def tzname(self, dt):
            return "UTC"

        def dst(self, dt):
            return self.ZERO

    utc = UTC()


def which(cmd, env=None):
    env = env or os.environ
    if cmd.startswith("/"):
        if os.access(cmd, os.X_OK) and os.path.isfile(cmd):
            return cmd
        return None

    paths = env.get("PATH").split(os.pathsep)
    for path in paths:
        c = os.path.join(path, cmd)
        if os.access(c, os.X_OK) and os.path.isfile(c):
            return c
    return None


class KeyPassingDefaultDict(collections.defaultdict):
    """ A default dict that passes the key to its factory function. """

    def __init__(self, *args, **kwargs):
        super(KeyPassingDefaultDict, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        if self.default_factory:
            self[key] = self.default_factory(key)
            return self[key]
        else:
            return super(KeyPassingDefaultDict, self).__missing__(key)


def enum(*e):
    enums = dict(zip(e, range(len(e))))
    return type("Enum", (), enums)


def defaults(default=None):
    """
    Catches any exception thrown by the wrapped function and returns `default`
    instead.

    Parameters
    ----------

    default : object
        The default value to return if the wrapped function throws an exception
    """
    def _f(func):
        @functools.wraps(func)
        def __f(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception:
                return default
        return __f
    return _f


def keys_in(items, *args):
    """
    Use this utility function to ensure multiple keys are in one or more
    dicts.  Returns `True` if all keys are present in at least one of the
    given dicts, otherwise returns `False`.

    :Parameters:
        - `items`: Iterable of required keys
        - Variable number of subsequent arguments, each one being a dict to check.
    """

    found = dict((key, False) for key in items)
    for d in args:
        for item in items:
            if not found[item] and item in d:
                found[item] = True
    return all(found.values())


def logging_level(logger, level):
    def _f(func):
        @functools.wraps(func)
        def check_log_level(*args, **kwargs):
            if logger.getEffectiveLevel() <= level:
                return func(*args, **kwargs)

        return check_log_level

    return _f


def deprecated(func, solution):
    """
    Mark a parser or combiner as deprecated, and give a message of how to fix
    this.  This will emit a warning in the logs when the function is used.
    When combined with modifications to conftest, this causes deprecations to
    become fatal errors when testing, so they get fixed.

    Arguments:
        func (function): the function or method being deprecated.
        solution (str): a string describing the replacement class, method or
            function that replaces the thing being deprecated.  For example,
            "use the `fnord()` function" or "use the `search()` method with
            the parameter `name='(value)'`".
    """

    def get_name_line(src):
        for line in src:
            if "@" not in line:
                return line.strip()

    path = inspect.getsourcefile(func)
    src, line_no = inspect.getsourcelines(func)
    name = get_name_line(src) or "Unknown"
    the_msg = "<{c}> at {p}:{l} is deprecated: {s}".format(
        c=name, p=path, l=line_no, s=solution
    )

    warnings.warn(the_msg, DeprecationWarning)


def make_iter(item):
    if isinstance(item, list):
        return item
    else:
        return [item]


def ensure_dir(path, dirname=False):
    log = logging.getLogger(__name__)
    try:
        if dirname:
            path = os.path.dirname(path)
        log.debug("Ensure dir '%s'", path)
        os.makedirs(path)
    except Exception as e:
        if log.level <= logging.DEBUG:
            log.debug("Failed to ensure dir: %s", e)
        return False
    return True


def _create_log_record(msg, date, level, machine_id):
    log_record = logging.LogRecord("upload_client", logging.getLevelName(level),
                                   machine_id, None, msg.strip(), None, None)
    log_record.asctime = date
    return log_record


class objectview(object):
    def __init__(self, dict_):
        self.__dict__ = dict_


def parse_keypair_lines(content, delim='|', kv_sep='='):
    """
    Parses a set of entities, where each entity is a set of key-value pairs
    contained all on one line.  Each entity is parsed into a dictionary and
    added to the list returned from this function.
    """
    r = []
    if content:
        for row in [line for line in content if line]:
            item_dict = {}
            for item in row.split(delim):
                key, value = [i.strip("'\"").strip() for i in item.strip().split(kv_sep)]
                item_dict[key] = value
            r.append(item_dict)
    return r


def rsplit(_str, seps):
    """
    Splits _str by the first sep in seps that is found from the right side.
    Returns a tuple without the separator.
    """
    for idx, ch in enumerate(reversed(_str)):
        if ch in seps:
            return _str[0:-idx - 1], _str[-idx:]


def check_path(path):
    found = os.path.exists(path)
    logger.debug("Checking for path [%s], found = %s.", path, found)
    return found


def get_addr():
    from insights.settings import web as config

    return "http://%s:%s" % (platform.node(), config["port"])


def get_path_for_system_id(category, system_id):
    return os.path.join(TMP_DIR, category, system_id[:2], system_id)


def word_wrap(line, wrap_len=72):
    if len(line) > wrap_len:
        for i, c in enumerate(reversed(line[:wrap_len])):
            if c == " ":
                break_point = wrap_len - i
                yield line[:break_point].strip()
                for more in word_wrap(line[break_point:], wrap_len):
                    yield more
                break
    else:
        yield line.strip()


def case_variants(*elements):
    """
    For configs which take case-insensitive options, it is necessary to extend the list with
    various common case variants (all combinations are not practical). In the future, this should
    be removed, when parser filters are made case-insensitive.

    Args:
        *elements (str): list of elements which need case-sensitive expansion, you should use
                         default case such as `Ciphers`, `MACs`, `UsePAM`, `MaxAuthTries`

    Returns:
        list: list of all expanded elements
    """
    expanded_list = []
    for element in elements:
        low = element.lower()
        up = element.upper()
        title = element.title()

        # Inner case conversion, such as `MACs` or `UsePAM` to `Macs` and `UsePam`
        converted = []
        for i, letter in enumerate(element):
            if i == 0:
                converted.append(letter)
            else:
                if element[i - 1].isupper():
                    converted.append(letter.lower())
                else:
                    converted.append(letter)
        converted = "".join(converted)

        for new_element in (element, converted, low, up, title):
            if new_element not in expanded_list:
                expanded_list.append(new_element)

    return expanded_list
