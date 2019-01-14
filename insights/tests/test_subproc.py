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
