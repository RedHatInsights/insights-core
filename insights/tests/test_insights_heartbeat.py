import unittest

from insights.plugins import insights_heartbeat
from insights.parsers.hostname import Hostname
from insights.core.plugins import make_response
from insights.tests import context_wrap

NON_MATCHING_HOSTNAME = "some-other-hostname-that-doesnt-match"

good = Hostname(context_wrap(insights_heartbeat.HOST))
bad = Hostname(context_wrap(NON_MATCHING_HOSTNAME))


class TestInsightsHeartbeat(unittest.TestCase):
    def test_heartbeat(self):
        expected_result = make_response(insights_heartbeat.ERROR_KEY)
        self.assertEquals(expected_result, insights_heartbeat.is_insights_heartbeat({Hostname: good}))
        self.assertEquals(None, insights_heartbeat.is_insights_heartbeat({Hostname: bad}))
