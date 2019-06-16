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

from insights.parsers import dcbtool_gc_dcb
from insights.tests import context_wrap


DCBTOOL_GC_OUTPUT = """

    Command:    Get Config
    Feature:    DCB State
    Port:       eth0
    Status:     Off
    DCBX Version: FORCED CIN

"""

DCBTOOL_GC_DCB_FAILED = """
connect: Connection refused
Failed to connect to lldpad - clif_open: Connection refused
"""


def test_dcbtool_gc():
    result = dcbtool_gc_dcb.Dcbtool(context_wrap(DCBTOOL_GC_OUTPUT))
    assert len(result.data) == 5
    assert result["command"] == "Get Config"
    assert result["feature"] == "DCB State"
    assert result["port"] == "eth0"
    assert result["status"] == "Off"
    assert result["dcbx_version"] == "FORCED CIN"

    assert not result.is_on

    result = dcbtool_gc_dcb.Dcbtool(context_wrap(DCBTOOL_GC_DCB_FAILED))
    assert len(result.data) == 0
