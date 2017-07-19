import unittest

from insights.plugins import insights_heartbeat
from insights.parsers.hostname import Hostname
from insights.core.plugins import make_response
from insights.tests import archive_provider, context_wrap, InputData


NON_MATCHING_HOSTNAME = "some-other-hostname-that-doesnt-match"

good = Hostname(context_wrap(insights_heartbeat.HOST))
bad = Hostname(context_wrap(NON_MATCHING_HOSTNAME))


class TestInsightsHeartbeat(unittest.TestCase):
    def test_heartbeat(self):
        expected_result = make_response(insights_heartbeat.ERROR_KEY)
        self.assertEquals(expected_result, insights_heartbeat.is_insights_heartbeat({Hostname: good}))
        self.assertEquals(None, insights_heartbeat.is_insights_heartbeat({Hostname: bad}))


@archive_provider(insights_heartbeat.is_insights_heartbeat)
def integration_tests():
    input_data = InputData(name="Match: no kernel", hostname=insights_heartbeat.HOST)
    expected = make_response(insights_heartbeat.ERROR_KEY)
    yield input_data, [expected]

    input_data = InputData(name="No Match: bad hostname", hostname=NON_MATCHING_HOSTNAME)
    yield input_data, [None]
