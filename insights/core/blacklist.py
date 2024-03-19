BLACKLISTED_SPECS = []
_FILE_FILTERS = set()
_COMMAND_FILTERS = set()
_PATTERN_FILTERS = set()
_KEYWORD_FILTERS = set()


def add_file(f):
    _FILE_FILTERS.add(f)


def add_command(f):
    _COMMAND_FILTERS.add(f)


def add_pattern(f):
    _PATTERN_FILTERS.add(f)


def add_keyword(f):
    _KEYWORD_FILTERS.add(f)


def allow_file(c):
    cl = len(c)
    return not any(c.startswith(f) and (cl == len(f) or c[len(f)] == ' ') for f in _FILE_FILTERS)


def allow_command(c):
    cl = len(c)
    return not any(c.startswith(f) and (cl == len(f) or c[len(f)] == ' ') for f in _COMMAND_FILTERS)


def get_disallowed_patterns():
    return _PATTERN_FILTERS


def get_disallowed_keywords():
    return _KEYWORD_FILTERS
