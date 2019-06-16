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

from insights.parsers.current_clocksource import CurrentClockSource
from insights.tests import context_wrap

CLKSRC = """
tsc
"""


def test_get_current_clksr():
    clksrc = CurrentClockSource(context_wrap(CLKSRC))
    assert clksrc.data == "tsc"
    assert clksrc.is_kvm is False
    assert clksrc.is_vmi_timer != clksrc.is_tsc
