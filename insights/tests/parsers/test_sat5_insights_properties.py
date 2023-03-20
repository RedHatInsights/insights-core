import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import sat5_insights_properties
from insights.parsers.sat5_insights_properties import Sat5InsightsProperties
from insights.tests import context_wrap

INSIGHTS_PROPERTIES = """
portalurl = https://cert-api.access.redhat.com/r/insights
enabled = true
debug = true
rpmname = redhat-access-insights
""".strip()


def test_insights_properties():
    result = Sat5InsightsProperties(context_wrap(INSIGHTS_PROPERTIES))
    assert result["enabled"] == 'true'
    assert result.enabled is True
    assert result.get("debug") == 'true'
    assert result.get("rpmname") == 'redhat-access-insights'
    assert result["rpmname"] == 'redhat-access-insights'


def test_doc():
    env = {
            'insights_props': Sat5InsightsProperties(context_wrap(INSIGHTS_PROPERTIES)),
          }
    failed, total = doctest.testmod(sat5_insights_properties, globs=env)
    assert failed == 0


def test_AB():
    with pytest.raises(SkipComponent):
        Sat5InsightsProperties(context_wrap(''))
