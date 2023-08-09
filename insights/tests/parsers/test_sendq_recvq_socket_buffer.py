import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import sendq_recvq_socket_buffer
from insights.parsers.sendq_recvq_socket_buffer import RecvQSocketBuffer, SendQSocketBuffer
from insights.tests import context_wrap

SENDQ_SOCKET_BUFFER = """
4096	16384	4194304
""".strip()

EMPTY_SENDQ_SOCKET_BUFFER = """
""".strip()

RECVQ_SOCKET_BUFFER = """
4096	87380	6291456
""".strip()

EMPTY_RECVQ_SOCKET_BUFFER = """
""".strip()


def test_empty_sendq_socket_buffer():
    with pytest.raises(ParseException) as exc:
        SendQSocketBuffer(context_wrap(EMPTY_SENDQ_SOCKET_BUFFER))
    assert str(exc.value) == "Empty content"


def test_sendq_socket_buffer():
    sendq_buffer = SendQSocketBuffer(context_wrap(SENDQ_SOCKET_BUFFER))
    assert sendq_buffer.minimum == 4096
    assert sendq_buffer.default == 16384
    assert sendq_buffer.maximum == 4194304
    assert sendq_buffer.raw == '4096 16384 4194304'


def test_empty_recvq_socket_buffer():
    with pytest.raises(ParseException) as exc:
        RecvQSocketBuffer(context_wrap(EMPTY_RECVQ_SOCKET_BUFFER))
    assert str(exc.value) == "Empty content"


def test_recvq_socket_buffer():
    recvq_buffer = RecvQSocketBuffer(context_wrap(RECVQ_SOCKET_BUFFER))
    assert recvq_buffer.minimum == 4096
    assert recvq_buffer.default == 87380
    assert recvq_buffer.maximum == 6291456
    assert recvq_buffer.raw == '4096 87380 6291456'


def test_doc():
    env = {
            'sendq_buffer_values': SendQSocketBuffer(context_wrap(SENDQ_SOCKET_BUFFER)),
            'recvq_buffer_values': RecvQSocketBuffer(context_wrap(RECVQ_SOCKET_BUFFER)),
          }
    failures, tests = doctest.testmod(sendq_recvq_socket_buffer, globs=env)
    assert failures == 0
