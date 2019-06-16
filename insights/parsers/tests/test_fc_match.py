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

from insights.parsers.fc_match import FCMatch
from insights.tests import context_wrap

FCMATCH_V1 = """
Pattern has 2 elts (size 16)
    family: "DejaVu Sans"(s)
    fontformat: "TrueType"(w)

Pattern has 2 elts (size 16)
    family: "DejaVu Sans"(s)
    fontformat: "TrueType"(w)

Pattern has 2 elts (size 16)
    family: "DejaVu Sans"(s)
    fontformat: "TrueType"(w)

Pattern has 2 elts (size 16)
    family: "Nimbus Sans L"(s)
    fontformat: "Type 1"(s)

Pattern has 2 elts (size 16)
    family: "Standard Symbols L"(s)
    fontformat: "Type 1"(s)
"""


def test_fcmatch_v1():
    fc_match = FCMatch(context_wrap(FCMATCH_V1))
    assert fc_match.data == [{'fontformat': '"TrueType"(w)', 'family': '"DejaVu Sans"(s)'},
                             {'fontformat': '"Type 1"(s)', 'family': '"Nimbus Sans L"(s)'},
                             {'fontformat': '"Type 1"(s)', 'family': '"Standard Symbols L"(s)'}]
    assert fc_match[0] == {'fontformat': '"TrueType"(w)', 'family': '"DejaVu Sans"(s)'}
    for item in fc_match:
        if item["family"] == '"DejaVu Sans"(s)':
            assert item["fontformat"] == '"TrueType"(w)'
