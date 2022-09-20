# -*- coding: UTF-8 -*-
import sys
import pytest
import shlex

from insights.core.spec_factory import SAFE_ENV
from insights.util import subproc


def test_call():
    result = subproc.call('echo -n hello')
    assert result == 'hello'


@pytest.mark.skipif(sys.version_info < (3, 6), reason="No need encode() for python3+.")
def test_call_SAFE_ENV_py3():
    # Test non-alphanumeric character
    result = subproc.call(u"echo -n '\xae'", env=SAFE_ENV)
    assert result == u'®'
    assert result == u'\xae'

    result = subproc.call(u"echo -n '®'", env=SAFE_ENV)
    assert result == u'®'
    assert result == u'\xae'


@pytest.mark.skipif(sys.version_info >= (3, 6), reason="Need encode() for python2.")
def test_call_SAFE_ENV_py2():
    # Test non-alphanumeric character
    result = subproc.call(u"echo -n '\xae'".encode('utf-8'), env=SAFE_ENV)
    assert result == u'®'
    assert result == u'\xae'

    result = subproc.call(u"echo -n '®'".encode('utf-8'), env=SAFE_ENV)
    assert result == u'®'
    assert result == u'\xae'


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
