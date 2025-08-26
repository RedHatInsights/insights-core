import os
import pytest
import shlex
import sys
import stat

from insights.core.exceptions import CalledProcessError
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
        with pytest.raises(CalledProcessError):
            subproc.call('sleep 3', timeout=1)


SCRIPT_CONTENT = """
#!/bin/bash
echo '0123456789'
exit 1
""".strip()


@pytest.fixture(scope="module")
def tmp_script(tmpdir_factory):
    root = str(tmpdir_factory.mktemp("test_subproc"))
    file_path = os.path.join(root, 'tmp.sh')
    with open(file_path, 'w') as fd:
        for line in SCRIPT_CONTENT.splitlines():
            fd.write(line + '\n')
    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)
    return file_path


def test_call_error_output(tmp_script):
    env = os.environ
    env.update(MAX_FAILURE_OUTPUT="6")
    with pytest.raises(CalledProcessError) as cpe:
        subproc.call(tmp_script, env=env)
    assert "012345" in str(cpe)
    assert "0123456" not in str(cpe)
