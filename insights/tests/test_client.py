import unittest
from insights.client import InsightsClientApi
from insights import get_nvr
from insights.client.constants import InsightsConstants as constants


class TestClient(unittest.TestCase):

    client = InsightsClientApi()

    def test_version(self):
        result = self.client.version()
        expected = {'core': get_nvr(), 'client_api': constants.version}
        self.assertEquals(result, expected)
