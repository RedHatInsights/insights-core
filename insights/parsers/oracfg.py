"""
oracle - File initSID.ora/spfileSID.ora
===============================================================================

This module provides plugins access to settings contained in oracle database
configuration files. The typical contents of these config files follow key =
value conventions::

    db_name = 'orcl'
    sga_target = 15G
    db_recovery_file_dest='/u01/app/oracle/fast_recovery_area'

Configuration is exposed via dictionary at ``obj.data`` with additional
pertinent information available via module properties.


Examples:
    >>> oracfg = shared[OracleConfig]
    >>> oracfg.db_name
    'orcl'
    >>> oracfg.amm_enabled
    True
    >> vars = oracfg.data
    >> vars.get['sga_target']
    '15G'
"""

import re
from string import whitespace
from .. import Parser, parser, get_active_lines
from insights.util import deprecated

# spfiles tend to contain strings of control characters usually bounded by 'C"'
# and always ending with an ASCII NULL. This regex describes those strings for
# removal
CLEANUP = re.compile('(C")?[\01\00].*\00')

GRID_REGEX = re.compile(r'.grid.dbs.')
VERSION_REGEX = re.compile(r'(\d+\.*)+')
SPFILE_REGEX = re.compile(r'spfile.*ora$')
PFILE_REGEX = re.compile(r'init.*ora$')

SUFFIXES = {'k': 1, 'm': 2, 'g': 3}


def str_to_byte(byte_string):
    """Takes a string of format DDDD[K|M|G]? and converts it to a byte value"""
    if byte_string[-1].lower() in SUFFIXES:
        return (int(byte_string[:-1]) * (1024 ** SUFFIXES.get(byte_string[-1].lower())))
    else:
        try:
            out = int(byte_string)
        except ValueError:
            out = 0
    return out


@parser('config.ora')
class OracleConfig(Parser):
    """
    Parse Oracle database settings contained in a .ora config file.

    Attributes:
        dbname (str): Database name/SID as a string. ``None`` if database name
            left undefined in configuration.
        spfile (bool): ``True`` if configuration sourced from spfile.ora.
        pfile (bool): ``True`` if configuration sourced from init.ora.
        amm_enabled (bool): ``True`` if Automatic Memory Management enabled in
            configuration.
        db_version (str): Database version number as a string. Sourced from
            configuration file path, ``None`` if path doesn't contain version
            string

    """
    def __init__(self, *args, **kwargs):
        deprecated(OracleConfig, "Use the parsers in the `oracle` module", pending=False)
        super(OracleConfig, self).__init__(*args, **kwargs)

    @property
    def dbname(self):
        return self.db_name

    @property
    def spfile(self):
        return self.sp_file

    @property
    def pfile(self):
        return self.p_file

    @property
    def amm_enabled(self):
        return self.amm

    @property
    def db_version(self):
        return self.dbversion

    def _parse_oracle_line(self, line):
        if '=' in line:
            (key, value) = line.split('=', 1)
            key = key.strip(whitespace + '"\'').lower()
            if ',' in line:
                value = [s.strip(whitespace + '"\'').lower() for s in value.split(',')]
            else:
                value = value.strip(whitespace + '"\'').lower()
            self.data[key] = value

            if self.dbversion:
                if int(self.dbversion.split('.')[0]) < 11 and key.endswith("sga_target") and str_to_byte(value) > 0:
                    self.amm = True
                elif key.endswith("memory_target") and str_to_byte(value) > 0:
                    self.amm = True

            if key.endswith("db_name"):
                self.db_name = value

    def parse_content(self, content):
        if GRID_REGEX.search(self.file_path):
            # Don't want grid product configs
            return

        self.db_name = None
        self.amm = False
        self.sp_file = bool(SPFILE_REGEX.search(self.file_name))
        self.p_file = bool(PFILE_REGEX.search(self.file_name))
        db_vers = VERSION_REGEX.search(self.file_path)
        if db_vers:
            self.dbversion = db_vers.group()
        else:
            self.dbversion = None
        self.data = {}

        for line in get_active_lines(content):
            # Check for NULL in line to begin control char removal
            if '\00' in line:
                line = CLEANUP.sub('', line)
            if '<ORACLE_BASE>' in line:
                # Default config file, ignore
                return
            self._parse_oracle_line(line)
