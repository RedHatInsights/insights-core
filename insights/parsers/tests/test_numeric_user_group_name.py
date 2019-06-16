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

from insights.parsers.numeric_user_group_name import NumericUserGroupName
from insights.tests import context_wrap
from insights.parsers import ParseException
from insights.core.plugins import ContentException

ZERO = """
/etc/passwd:0
/etc/group:0
""".strip()

NONZERO_1 = """
/etc/passwd:3
/etc/group:0
""".strip()

NONZERO_2 = """
/etc/passwd:0
/etc/group:4
""".strip()

NONZERO_3 = """
/etc/passwd:1
/etc/group:1
""".strip()

UNSTRIPPED_ZERO = """

/etc/passwd:0
/etc/group:0

"""
UNSTRIPPED_NONZERO_1 = """

/etc/passwd:3
/etc/group:0

"""
UNSTRIPPED_NONZERO_2 = """

/etc/passwd:0
/etc/group:4

"""
UNSTRIPPED_NONZERO_3 = """

/etc/passwd:1
/etc/group:1

"""

# should produce no result
ERRORS_1 = """

/etc/passwd:1
/bin/grep: /etc/group: No such file or directory

"""

ERRORS_2 = """

/bin/grep: /etc/passwd: No such file or directory
/etc/group:1

"""

ERRORS_3 = """

/bin/grep: /etc/passwd: No such file or directory
/etc/group:0

"""

# should produce no result
ERRORS_4 = """

/bin/grep: /etc/passwd: No such file or directory
/bin/grep: /etc/group: No such file or directory

"""

# should produce no result
ERRORS_5 = """

/bin/grep: No such file or directory

"""

# Should produce a valid result because it contains valid lines.
# The last valid lines are used.
# /etc/passwd:1
# /etc/group:1
ERRORS_6 = """

/etc/passwd: d:
/etc/group: No such file or directory
/bin/group:7
/bin/etc/group:7
/bin/grep: No such file or directory
# should be ignored:
/etc/passwd:0
# valid output for /etc/passwd on the following line:
/etc/passwd:1
/bin/group:4
/bin/gry
# should be ignored
/etc/group:0
# valid output for /etc/group on the following line:
/etc/group:1
/bin/grep: /etc/passwd:3
"""


def test_numeric_user_group_name_1():
    for data in [ZERO, UNSTRIPPED_ZERO]:
        numeric_user_group_name = NumericUserGroupName(context_wrap(data))
        assert not numeric_user_group_name.has_numeric_user_or_group


def test_numeric_user_group_name_2():
    for data in [NONZERO_1, NONZERO_2, NONZERO_3, UNSTRIPPED_NONZERO_1, UNSTRIPPED_NONZERO_2,
                 UNSTRIPPED_NONZERO_3, ERRORS_6]:
        numeric_user_group_name = NumericUserGroupName(context_wrap(data))
        assert numeric_user_group_name.has_numeric_user_or_group


def test_numeric_user_group_name_6():
    for data in [NONZERO_1, UNSTRIPPED_NONZERO_1]:
        numeric_user_group_name = NumericUserGroupName(context_wrap(data))
        assert numeric_user_group_name.nr_numeric_user == 3
        assert numeric_user_group_name.nr_numeric_group == 0


def test_numeric_user_group_name_7():
    for data in [NONZERO_2, UNSTRIPPED_NONZERO_2]:
        numeric_user_group_name = NumericUserGroupName(context_wrap(data))
        assert numeric_user_group_name.nr_numeric_user == 0
        assert numeric_user_group_name.nr_numeric_group == 4


def test_numeric_user_group_name_8():
    for data in [NONZERO_3, UNSTRIPPED_NONZERO_3, ERRORS_6]:
        numeric_user_group_name = NumericUserGroupName(context_wrap(data))
        assert numeric_user_group_name.nr_numeric_user == 1
        assert numeric_user_group_name.nr_numeric_group == 1


def test_numeric_user_group_name_9():
    for data in [ERRORS_1, ERRORS_2, ERRORS_3, ERRORS_4]:
        try:
            NumericUserGroupName(context_wrap(data))
            assert False
        except ParseException:
            assert True


def test_numeric_user_group_name_10():
    try:
        NumericUserGroupName(context_wrap(ERRORS_5))
        assert False
    except ContentException:
        assert True
