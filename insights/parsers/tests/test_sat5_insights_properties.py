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

import pytest
import doctest
from insights.tests import context_wrap
from insights.parsers import sat5_insights_properties, SkipException
from insights.parsers.sat5_insights_properties import Sat5InsightsProperties

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
    with pytest.raises(SkipException):
        Sat5InsightsProperties(context_wrap(''))
