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
from insights.parsers.sysconfig import VirtWhoSysconfig

VIRTWHO = """
# Register ESX machines using vCenter
#VIRTWHO_ESX=0
# Register guests using RHEV-M
 VIRTWHO_RHEVM=1

# Options for RHEV-M mode
VIRTWHO_RHEVM_OWNER=

TEST_OPT="A TEST"
""".strip()


def test_sysconfig_virt_who():
    result = VirtWhoSysconfig(context_wrap(VIRTWHO))
    assert result["VIRTWHO_RHEVM"] == '1'
    assert result["VIRTWHO_RHEVM_OWNER"] == ''
    assert result.get("NO_SUCH_OPTIONS") is None
    assert "NOSUCHOPTIONS" not in result
    assert result.get("TEST_OPT") == 'A TEST'
