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
from insights.parsers.host_vdsm_id import VDSMId

UUID = 'F7D9D983-6233-45C2-A387-9B0C33CB1306'

UUID_CONTENT = """
# VDSM UUID info
#
F7D9D983-6233-45C2-A387-9B0C33CB1306
""".strip()


def test_get_vdsm_id():
    expected = VDSMId(context_wrap(UUID_CONTENT))
    assert UUID == expected.uuid
