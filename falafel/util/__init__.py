import logging
import platform
import os

TMP_DIR = os.path.join("/tmp", "falafel-web")
logger = logging.getLogger(__name__)


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
        def check_log_level(*args, **kwargs):
            if logger.getEffectiveLevel() <= level:
                return func(*args, **kwargs)

        return check_log_level

    return _f


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


def parse_table(content, delim=None, max_splits=-1, strip=True):
    """
    Parses table-like text. Assumes the first
    row contains column names.
    """
    if not content:
        return []
    if strip:
        cols = [c.strip() for c in content[0].split(delim)]
    else:
        cols = content[0].split(delim)
    r = []
    for row in content[1:]:
        row = row.strip()
        if row:
            if strip:
                parsed = dict(zip(cols, [i.strip() for i in row.split(delim, max_splits)]))
            else:
                parsed = dict(zip(cols, row.split(delim, max_splits)))
            r.append(parsed)
    return r


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
    from falafel.web.settings import engine as config

    return "http://%s:%s" % (platform.node(), config["port"])


def get_path_for_system_id(category, system_id):
    return os.path.join(TMP_DIR, category, system_id[:2], system_id)
