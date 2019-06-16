#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
WIP: Will require tweaks as additional Oracle functionality is added.

Curently only gathers information from a database using generic init.ora file.
"""

import re
from string import whitespace
from .. import Parser, parser, get_active_lines
from insights.specs import Specs

# spfiles tend to contain strings of control characters usually bounded by 'C"'
# and always ending with an ASCII NULL. This regex describes those strings for
# removal
cleanup = re.compile('(C")?[\01\00].*\00')


def _parse_oracle(lines):
    """
    Performs the actual file parsing, returning a dict of the config values
    in a given Oracle DB config file.

    Despite their differences, the two filetypes are similar enough to
    allow idential parsing.
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


@parser(Specs.init_ora)
class OraclePfile(Parser):
    """
    Parse Oracle database settings contained in an init.ora file.

    Returns a dict containing the name and pertinent settings of the database.

    Future iterations may have to check multiple .ora files for multiple DBs.
    """

    def parse_content(self, content):
        self.data = dict(_parse_oracle(content))


@parser(Specs.spfile_ora)
class OracleSpfile(Parser):
    """
    Parse Oracle database settings contained in an spfile.

    Returns a dict containing the name and pertinent settings of the database.
    """

    def parse_content(self, content):
        self.data = dict(_parse_oracle(content))
