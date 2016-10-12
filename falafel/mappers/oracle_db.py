"""
WIP: Will require tweaks as additional Oracle functionality is added.

Curently only gathers information from a database using generic init.ora file.
"""

import re
from string import whitespace
from .. import mapper, get_active_lines

# spfiles tend to contain strings of control characters usually bounded by 'C"'
# and always ending with an ASCII NULL. This regex describes those strings for
# removal
cleanup = re.compile('(C")?[\01\00].*\00')


def parse_oracle(lines):
    """
    Performs the actual file parsing, returning a dict of the config values in
    a given Oracle DB config file.

    Despite their differences, the two filetypes are similar enough to allow
    idential parsing.
    """
    config = {}

    for line in get_active_lines(lines):
        # Check for NULL in line to begin control char removal
        if '\00' in line:
            line = cleanup.sub('', line)
        if '=' in line:
            (key, value) = line.split('=', 1)
            key = key.strip(whitespace + '"\'').lower()
            if ',' in line:
                value = [s.strip(whitespace + '"\'').lower() for s in value.split(',')]
            else:
                value = value.strip(whitespace + '"\'').lower()
            config[key] = value

    return config


@mapper('init.ora')
def oracle_pfile(context):
    """
    Parse Oracle database settings contained in an init.ora file.

    Returns a dict containing the name and pertinent settings of the database.

    Future iterations may have to check multiple .ora files for multiple DBs.
    """

    return parse_oracle(context.content)


@mapper('spfile.ora')
def oracle_spfile(context):
    """
    Parse Oracle database settings contained in an spfile.

    Returns a dict containing the name and pertinent settings of the database.
    """

    return parse_oracle(context.content)
