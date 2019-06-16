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

from .. import parser, LegacyItemAccess, CommandParser
from insights.specs import Specs


@parser(Specs.rhn_charsets)
class RHNCharSets(LegacyItemAccess, CommandParser):
    """
    ==== Sample (1) embedded database ====
     server_encoding
    -----------------
     UTF8
    (1 row)

     client_encoding
    -----------------
     UTF8
    (1 row)
    ==== Sample (2) Oracle database ====
    PARAMETER                  VALUE
    ---------------------------------
    NLS_CHARACTERSET           UTF8
    NLS_NCHAR_CHARACTERSET     UTF8
    ======================================
    Returns a dict:
    - {'server_encoding': 'UTF8','client_encoding': 'UTF8'}
    - {'NLS_CHARACTERSET': 'UTF8','NLS_NCHAR_CHARACTERSET': 'UTF8'}
    """

    def parse_content(self, content):
        db_set = {}
        db_backend = None
        in_server = False
        in_client = False
        for line in content:
            line = line.strip()
            # skip empty and useless lines
            if not line or line.startswith(('----', '(', 'PARAMETER')):
                continue
            if '_encoding' in line:
                db_backend = 'postgresql'
                in_server = line.startswith('server_')
                in_client = line.startswith('client_')
            elif db_backend == 'postgresql':
                if in_server:
                    db_set['server_encoding'] = line
                elif in_client:
                    db_set['client_encoding'] = line
            elif line.startswith('NLS_'):
                line_splits = line.split()
                if len(line_splits) == 2:
                    db_set[line_splits[0]] = line_splits[1]
        self.data = db_set
