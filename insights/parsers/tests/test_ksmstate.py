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

from insights.parsers import ksmstate
from insights.tests import context_wrap

KSMSTATE0 = "0"
KSMSTATE1 = "1"


def test_is_running_0():
    ksm_info = ksmstate.is_running(context_wrap(KSMSTATE0))
    assert ksm_info.get('running') is False


def test_is_running_1():
    ksm_info = ksmstate.is_running(context_wrap(KSMSTATE1))
    assert ksm_info.get('running') is True
