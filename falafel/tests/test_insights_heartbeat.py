import unittest

from falafel.plugins import insights_heartbeat
from falafel.core.plugins import make_response
from falafel.tests import context_wrap

NON_MATCHING_HOSTNAME = "some-other-hostname-that-doesnt-match"

class TestInsightsHeartbeat(unittest.TestCase):
    def test_heartbeat(self):
        expected_result = make_response(insights_heartbeat.ERROR_KEY)
        self.assertEquals(expected_result, insights_heartbeat.is_insights_heartbeat(context_wrap(insights_heartbeat.HOST)))
        self.assertEquals(None, insights_heartbeat.is_insights_heartbeat(context_wrap(NON_MATCHING_HOSTNAME)))
