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

from insights.tests import context_wrap
from insights.parsers.rhn_charsets import RHNCharSets


emb_charsets_content = """
 server_encoding
-----------------
 UTF~
(1 row)

 client_encoding
-----------------
 UTF8
(1 row)
"""

ora_charsets_content = """
PARAMETER                  VALUE
---------------------------------
NLS_CHARACTERSET           UTF8
NLS_NCHAR_CHARACTERSET     UTF8
"""


def test_embedded_db():
    result = RHNCharSets(context_wrap(emb_charsets_content))
    assert result.get('server_encoding') == 'UTF~'
    assert result.get('client_encoding') == 'UTF8'


def test_oracle_db():
    result = RHNCharSets(context_wrap(ora_charsets_content))
    assert result.get('NLS_CHARACTERSET') == 'UTF8'
    assert result.get('NLS_NCHAR_CHARACTERSET') == 'UTF8'
