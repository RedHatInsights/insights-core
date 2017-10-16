import sys

from insights.client import InsightsClient
from insights import package_info


def test_version():

    # Hack to prevent client from parsing args to py.test
    tmp = sys.argv
    sys.argv = []

    try:
        client = InsightsClient(logging_file='/tmp/insights.log')
        result = client.version()
        assert result == "%s-%s" % (package_info["VERSION"], package_info["RELEASE"])
    finally:
        sys.argv = tmp
