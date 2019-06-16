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

from insights.parsers.tmpfilesd import TmpFilesD
from insights.tests import context_wrap

SAP_CONF = """
# systemd tmpfiles exclude file for SAP
# SAP software stores some important files
# in /tmp which should not be deleted

# Exclude SAP socket and lock files
x /tmp/.sap*

# Exclude HANA lock file
x /tmp/.hdb*lock
""".strip()


def test_tmpfilesd():
    ctx = context_wrap(SAP_CONF, path='/etc/tmpfiles.d/sap.conf')
    data = TmpFilesD(ctx)

    assert len(data.files) == 2
    assert data.files == ['/tmp/.sap*', '/tmp/.hdb*lock']
    assert data.rules == [{'type': 'x',
                           'mode': None,
                           'path': '/tmp/.sap*',
                           'uid': None,
                           'gid': None,
                           'age': None,
                           'argument': None},
                          {'type': 'x',
                           'path': '/tmp/.hdb*lock',
                           'mode': None,
                           'uid': None,
                           'gid': None,
                           'age': None,
                           'argument': None}]
    assert data.file_path == '/etc/tmpfiles.d/sap.conf'
    assert data.file_name == 'sap.conf'


def test_find_file():
    ctx = context_wrap(SAP_CONF, path='/etc/tmpfiles.d/sap.conf')
    data = TmpFilesD(ctx)

    assert data.find_file('.sap*') == [{'path': '/tmp/.sap*', 'type': 'x', 'mode': None,
                                        'age': None, 'gid': None, 'uid': None,
                                        'argument': None}]
    assert data.find_file('.hdb*lock') == [{'path': '/tmp/.hdb*lock', 'type': 'x',
                                            'mode': None, 'uid': None, 'gid': None,
                                            'age': None, 'argument': None}]
    assert data.find_file('bar') == []
