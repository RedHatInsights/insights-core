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

from insights.parsers.sysconfig import CorosyncSysconfig
from insights.tests import context_wrap

corosync_content = """
# Corosync init script configuration file

# COROSYNC_INIT_TIMEOUT specifies number of seconds to wait for corosync
# initialization (default is one minute).
COROSYNC_INIT_TIMEOUT=60

# COROSYNC_OPTIONS specifies options passed to corosync command
# (default is no options).
# See "man corosync" for detailed descriptions of the options.
COROSYNC_OPTIONS=""
"""


def test_corosync_sysconfig():
    result = CorosyncSysconfig(context_wrap(corosync_content))
    assert result.data['COROSYNC_OPTIONS'] == ""
    assert result.data['COROSYNC_INIT_TIMEOUT'] == "60"

    assert result.options == ''
    assert result.unparsed_lines == []
