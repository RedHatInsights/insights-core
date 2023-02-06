import re


BLACKLISTED_SPECS = []
_FILE_FILTERS = set()
_COMMAND_FILTERS = set()
_PATTERN_FILTERS = set()
_KEYWORD_FILTERS = set()


def add_file(f):
    _FILE_FILTERS.add(re.compile(f))


def add_command(f):
    _COMMAND_FILTERS.add(re.compile(f))


def add_pattern(f):
    _PATTERN_FILTERS.add(f)


def add_keyword(f):
    _KEYWORD_FILTERS.add(f)


def allow_file(c):
    return not any(f.match(c) for f in _FILE_FILTERS)


def allow_command(c):
    return not any(f.match(c) for f in _COMMAND_FILTERS)


def get_disallowed_patterns():
    return _PATTERN_FILTERS


def get_disallowed_keywords():
    return _KEYWORD_FILTERS
