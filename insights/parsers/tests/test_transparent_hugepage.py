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

from insights.parsers.transparent_hugepage import ThpEnabled, ThpUseZeroPage
from insights.tests import context_wrap

ZEROPAGE_0 = "0"
ZEROPAGE_1 = "1"
ZEROPAGE_INVALID = """
bla
ble
asdf


"""

ENABLED_INVALID = """

asdf fda asdfdsaf
"""

ENABLED_MADVISE = """
always [madvise] never
"""

ENABLED_NEVER = """
always madvise [never]
"""

# testing without newlines
ENABLED_ALWAYS = """[always] madvise never"""


def test_zeropage():
    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_0))
    assert conf is not None
    assert "0" == conf.use_zero_page

    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_1))
    assert conf is not None
    assert "1" == conf.use_zero_page

    conf = ThpUseZeroPage(context_wrap(ZEROPAGE_INVALID))
    assert conf is not None
    assert ZEROPAGE_INVALID.replace("\n", " ").strip() == conf.use_zero_page


def test_enabled():
    conf = ThpEnabled(context_wrap(ENABLED_INVALID))
    assert conf is not None
    assert None is conf.active_option
    assert ENABLED_INVALID.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_MADVISE))
    assert conf is not None
    assert "madvise" == conf.active_option
    assert ENABLED_MADVISE.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_NEVER))
    assert conf is not None
    assert "never" == conf.active_option
    assert ENABLED_NEVER.strip() == conf.line

    conf = ThpEnabled(context_wrap(ENABLED_ALWAYS))
    assert conf is not None
    assert "always" == conf.active_option
    assert ENABLED_ALWAYS.strip() == conf.line
