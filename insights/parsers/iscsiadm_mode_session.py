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

"""
IscsiAdmModeSession - command ``iscsiadm - m session``
======================================================

This module provides the class ``IscsiAdmModeSession`` which processes
``iscsiadm -m session`` command output.  Typical output looks like::

    tcp: [1] 10.72.32.45:3260,1 iqn.2017-06.com.example:server1 (non-flash)
    tcp: [2] 10.72.32.45:3260,1 iqn.2017-06.com.example:server2 (non-flash)

The class has one attribute ``data`` which is a ``list`` representing each line
of the input data as a ``dict`` with keys corresponding to the keys in the output.

Examples:

    >>> iscsiadm_mode_session_content = '''
    ... tcp: [1] 10.72.32.45:3260,1 iqn.2017-06.com.example:server1 (non-flash)
    ... tcp: [2] 10.72.32.45:3260,1 iqn.2017-06.com.example:server2 (non-flash)
    ...'''.strip()

    >>> from insights.parsers.iscsiadm_mode_session import IscsiAdmModeSession
    >>> from insights.tests import context_wrap
    >>> shared = {IscsiAdmModeSession: IscsiAdmModeSession(context_wrap(iscsiadm_mode_session_content))}
    >>> result = shared[IscsiAdmModeSession]
    >>> result[0]
    {'IFACE_TRANSPORT': 'tcp', 'SID': '1', 'TARGET_IP': '10.72.32.45:3260,1',
     'TARGET_IQN': 'iqn.2017-06.com.example:server1'}
    >>> result[1]['TARGET_IQN']
    'iqn.2017-06.com.example:server2'
"""

from .. import parser, LegacyItemAccess, CommandParser
from insights.specs import Specs


@parser(Specs.iscsiadm_m_session)
class IscsiAdmModeSession(CommandParser, LegacyItemAccess):
    """Class to process the ``iscsiadm - m session`` command output.

    Attributes:

    data (list): A list containing a dictionary for each line of the output in the form::

            [
                {
                    'IFACE_TRANSPORT': "tcp",
                    'SID': '1',
                    'TARGET_IP': '10.72.32.45:3260,1',
                    'TARGET_IQN': 'iqn.2017-06.com.example:server1'
                },
                {
                    'IFACE_TRANSPORT': "tcp",
                    'SID': '2',
                    'TARGET_IP': '10.72.32.45:3260,1',
                    'TARGET_IQN': 'iqn.2017-06.com.example:server2'
                }
            ]
    """
    def parse_content(self, content):
        iscsiadm_session_all = []
        for line in (l.split() for l in content if l.strip()):
            iscsiadm_session_all.append({"IFACE_TRANSPORT": line[0].strip(':'),
                                         "SID": line[1].strip('[]'),
                                         "TARGET_IP": line[2],
                                         "TARGET_IQN": line[3]})

        self.data = iscsiadm_session_all
        """list of dict: List containing dict for each line of command output."""
