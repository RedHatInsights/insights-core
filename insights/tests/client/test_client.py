import sys

from insights.client import InsightsClient
from insights import get_nvr
from insights.client.constants import InsightsConstants as constants


def test_version():

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        client = InsightsClient(logging_file='/tmp/insights.log')
        result = client.version()
        expected = {'core': get_nvr(), 'client_api': constants.version}
        assert result == expected
    finally:
        sys.argv = tmp
