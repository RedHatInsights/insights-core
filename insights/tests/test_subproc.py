import pytest

from insights.util import subproc


def test_call():
    result = subproc.call('echo -n hello')
    assert result == 'hello'


def test_call_timeout():
    with pytest.raises(subproc.CalledProcessError):
        subproc.call('sleep 3', timeout=1)


def test_call_invalid_args():
    with pytest.raises(subproc.CalledProcessError):
        subproc.call([1, 2, 3])
