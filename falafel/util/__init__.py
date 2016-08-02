import logging
import os


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


def ensure_dir(path):
    log = logging.getLogger(__name__)
    try:
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


def parse_table(content, delim=None, max_splits=-1):
    """
    Parses table-like text. Assumes the first
    row contains column names.
    """
    if not content:
        return []
    cols = content[0].split(delim)
    return [dict(zip(cols, row.split(delim, max_splits))) for row in content[1:] if row.strip()]


def rsplit(_str, seps):
    """
    Splits _str by the first sep in seps that is found from the right side.
    Returns a tuple without the separator.
    """
    for idx, ch in enumerate(reversed(_str)):
        if ch in seps:
            return _str[0:-idx - 1], _str[-idx:]
