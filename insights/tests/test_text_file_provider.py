import pytest
from insights.core.spec_factory import ContentException, TextFileProvider


def test_command_not_found():
    bad_line = "blah: Command not found"
    with pytest.raises(ContentException):
        TextFileProvider.validate_lines([bad_line])


def test_no_such_file():
    bad_line = "timeout: failed to run command `/usr/sbin/brctl': No such file or directory"
    with pytest.raises(ContentException):
        TextFileProvider.validate_lines([bad_line])
