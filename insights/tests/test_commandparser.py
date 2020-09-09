from insights.core import CommandParser
from insights.tests import context_wrap
from insights.core.plugins import ContentException
import pytest

CMF = "blah: Command not found"
NO_FILES_FOUND = "No files found for docker.service"
NO_SUCH_FILE = "/usr/bin/blah: No such file or directory"
NOT_A_DIRECTORY = "/etc/mail/spamassassin/channel.d: Not a directory"
MULTI_LINE = """
blah: Command not found
/usr/bin/blah: No such file or directory
""".strip()
MULTI_LINE_BAD = """
Missing Dependencies:
    At Least One Of:
        insights.specs.default.DefaultSpecs.aws_instance_type
        insights.specs.insights_archive.InsightsArchiveSpecs.aws_instance_type
""".strip()


class MockParser(CommandParser):
    def parse_content(self, content):
        self.data = content


def test_command_not_found():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(CMF))
    assert "Command not found" in str(e.value)


def test_no_files_found():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(NO_FILES_FOUND))
    assert "No files found for" in str(e.value)


def test_no_such_file_or_directory():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(NO_SUCH_FILE))
    assert "No such file or directory" in str(e.value)


def test_not_a_directory():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(NOT_A_DIRECTORY))
    assert "Not a directory" in str(e.value)


def test_multi_line():
    assert MULTI_LINE.split('\n') == MockParser(context_wrap(MULTI_LINE)).data


def test_multi_line_ng():
    with pytest.raises(ContentException) as e:
        MockParser(context_wrap(MULTI_LINE_BAD))
    assert "Missing Dependencies:" in str(e.value)
