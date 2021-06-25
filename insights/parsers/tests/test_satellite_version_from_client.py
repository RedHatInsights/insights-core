from insights.tests import context_wrap
from insights.parsers.satellite_version_from_client import SatelliteVersionFromClient
from insights.parsers import satellite_version_from_client
from insights.parsers import SkipException
import pytest
import doctest


KATELLO_OUTPUT_66 = """
{"version":"3.12.0.32","timeUTC":"2021-05-27 02:04:55 UTC"}
""".strip()

KATELLO_OUTPUT_67 = """
{"version":"3.14.0.32","timeUTC":"2021-05-27 02:04:55 UTC"}
""".strip()

KATELLO_OUTPUT_69 = """
{"version":"3.18.1.22","timeUTC":"2021-05-20 13:59:20 UTC"}
""".strip()

NO_VERSION = """
{"bac":"3.14.0.32","timeUTC":"2021-05-27 02:04:55 UTC"}
""".strip()


def test_get_sat6_version():
    result = SatelliteVersionFromClient(context_wrap(KATELLO_OUTPUT_67))
    assert result.version == "6.7"
    assert result.major == 6
    assert result.minor == 7


def test_exception():
    with pytest.raises(SkipException):
        SatelliteVersionFromClient(context_wrap(KATELLO_OUTPUT_66))
    with pytest.raises(SkipException):
        SatelliteVersionFromClient(context_wrap(NO_VERSION))


def test_doc():
    api_output = satellite_version_from_client.SatelliteVersionFromClient(context_wrap(KATELLO_OUTPUT_69))
    globs = {
        'api_output': api_output
    }
    failed, tested = doctest.testmod(satellite_version_from_client, globs=globs)
    assert failed == 0
