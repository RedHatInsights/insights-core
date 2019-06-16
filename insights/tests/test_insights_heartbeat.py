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

from insights.core.plugins import make_fail
from insights.plugins import insights_heartbeat
from insights.parsers.hostname import Hostname
from insights.specs import Specs
from insights.tests import context_wrap, InputData, run_test


NON_MATCHING_HOSTNAME = "some-other-hostname-that-doesnt-match"

good = Hostname(context_wrap(insights_heartbeat.HOST))
bad = Hostname(context_wrap(NON_MATCHING_HOSTNAME))


def test_heartbeat():
    expected_result = make_fail(insights_heartbeat.ERROR_KEY)
    assert expected_result == insights_heartbeat.is_insights_heartbeat(good)
    assert insights_heartbeat.is_insights_heartbeat(bad) is None


def test_integration_tests():
    comp = insights_heartbeat.is_insights_heartbeat

    input_data = InputData(name="Match: no kernel")
    input_data.add(Specs.hostname, insights_heartbeat.HOST)
    expected = make_fail(insights_heartbeat.ERROR_KEY)
    run_test(comp, input_data, expected)

    input_data = InputData(name="No Match: bad hostname")
    input_data.add(Specs.hostname, NON_MATCHING_HOSTNAME)
    run_test(comp, input_data, None)
