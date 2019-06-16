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

from insights.core import CommandParser
from insights.tests import context_wrap
from insights.core.plugins import ContentException
import pytest

CMF = "blah: Command not found"
NO_SUCH_FILE = "/usr/bin/blah: No such file or directory"
MULTI_LINE = "blah: Command not found\n" \
             "/usr/bin/blah: No such file or directory"


class MockParser(CommandParser):
    def parse_content(self, content):
        self.data = content


def test_command_not_found():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(CMF))
    assert "Command not found" in str(e.value)


def test_no_such_file_or_directory():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(NO_SUCH_FILE))
    assert "No such file or directory" in str(e.value)


def test_multi_line():
    assert MULTI_LINE.split('\n') == MockParser(context_wrap(MULTI_LINE)).data
