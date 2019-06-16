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

from insights.parsers.iscsiadm_mode_session import IscsiAdmModeSession
from insights.tests import context_wrap

ISCSIADM_SESSION_INFO = """
tcp: [1] 10.72.32.45:3260,1 iqn.2017-06.com.example:server1 (non-flash)
tcp: [2] 10.72.32.45:3260,1 iqn.2017-06.com.example:server2 (non-flash)
""".strip()


EXPECTED_RESULTS = [{'IFACE_TRANSPORT': "tcp",
                      'SID': '1',
                      'TARGET_IP': '10.72.32.45:3260,1',
                      'TARGET_IQN': 'iqn.2017-06.com.example:server1'},
                     {'IFACE_TRANSPORT': "tcp",
                      'SID': '2',
                      'TARGET_IP': '10.72.32.45:3260,1',
                      'TARGET_IQN': 'iqn.2017-06.com.example:server2'}]


def test_iscsiadm_session_info():
    iscsiadm_session_info = IscsiAdmModeSession(context_wrap(ISCSIADM_SESSION_INFO))

    assert iscsiadm_session_info.data == EXPECTED_RESULTS
    assert len(iscsiadm_session_info.data) == 2
    assert iscsiadm_session_info[0] == {
        'IFACE_TRANSPORT': 'tcp',
        'SID': '1',
        'TARGET_IP': '10.72.32.45:3260,1',
        'TARGET_IQN': 'iqn.2017-06.com.example:server1'
    }
    assert iscsiadm_session_info[1]['TARGET_IQN'] == 'iqn.2017-06.com.example:server2'
