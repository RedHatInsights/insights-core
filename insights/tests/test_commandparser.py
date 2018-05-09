from insights.core import CommandParser
from insights.tests import context_wrap
from insights.parsers import ParseException
import pytest

CMF = "blah: Command not found"
NO_SUCH_FILE = "/usr/bin/blah: No such file or directory"


class MockParser(CommandParser):
    def parse_content(self, content):
        pass


def test_command_not_found():
    with pytest.raises(ParseException) as e:
        MockParser(context_wrap(CMF))
    assert "Command not found" in str(e.value)


def test_no_such_file_or_directory():
    with pytest.raises(ParseException) as e:
        MockParser(context_wrap(NO_SUCH_FILE))
    assert "No such file or directory" in str(e.value)
