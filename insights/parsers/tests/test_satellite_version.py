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

from insights.tests import context_wrap
from insights.parsers.satellite_version import Satellite6Version
from insights.parsers import ParseException
import pytest

satellite_version = """
COMMAND> cat /usr/share/foreman/lib/satellite/version.rb

module Satellite
  VERSION = "6.1.3"
end
"""

no_sat = """
scdb-1.15.8-1.el6sat.noarch                                 Wed May 18 14:48:14 2016
scl-utils-20120927-27.el6_6.x86_64                          Wed May 18 14:18:16 2016
SDL-1.2.14-6.el6.x86_64                                     Wed May 18 14:16:25 2016
"""


def test_get_sat6_version():
    result = Satellite6Version(context_wrap(satellite_version, path='satellite_version'))
    assert result.full == "6.1.3"
    assert result.version == "6.1.3"
    assert result.major == 6
    assert result.minor == 1
    assert result.release is None


def test_get_no_sat_version():
    with pytest.raises(ParseException) as e:
        Satellite6Version(context_wrap(no_sat, path='satellite_version'))
    assert "Cannot parse satellite version" in str(e)
