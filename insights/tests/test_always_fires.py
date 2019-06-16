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

from insights.core.plugins import make_pass
from insights.tests import InputData, run_test

from insights.plugins import always_fires


def test_always_fires():
    i = InputData()
    expected = make_pass("ALWAYS_FIRES", kernel="this is junk")
    run_test(always_fires.report, i, expected)
