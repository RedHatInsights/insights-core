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

import sys
import pytest
import shlex

from insights.util import subproc


def test_call():
    result = subproc.call('echo -n hello')
    assert result == 'hello'


def test_call_list_of_lists():
    cmd = "echo -n ' hello '"
    cmd = shlex.split(cmd)
    result = subproc.call([cmd, ["grep", "-F", "hello"]])
    assert "hello" in result


def test_call_timeout():
    # Timeouts don't work on OS X
    if sys.platform != "darwin":
        with pytest.raises(subproc.CalledProcessError):
            subproc.call('sleep 3', timeout=1)
