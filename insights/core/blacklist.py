import re


_COMMAND_FILTERS = set()
_FILE_FILTERS = set()


def add_command(f):
    _COMMAND_FILTERS.add(re.compile(f))


def add_file(f):
    _FILE_FILTERS.add(re.compile(f))


def allow_command(c):
    return not any(f.match(c) for f in _COMMAND_FILTERS)


def allow_file(c):
    return not any(f.match(c) for f in _FILE_FILTERS)
