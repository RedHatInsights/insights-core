import doctest
import pytest

from insights.core.exceptions import ContentException, SkipComponent
from insights.parsers import postconf
from insights.parsers.postconf import PostconfBuiltin, Postconf, _Postconf
from insights.tests import context_wrap

V_OUT1 = """
""".strip()

V_OUT2 = """
smtpd_tls_loglevel = 0
smtpd_tls_mandatory_ciphers = medium
smtpd_tls_mandatory_exclude_ciphers =
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3, !TLSv1
""".strip()

V_OUT3 = """
command not found
""".strip()


def test_PostconfBuiltin():
    with pytest.raises(SkipComponent):
        PostconfBuiltin(context_wrap(V_OUT1))

    with pytest.raises(ContentException):
        PostconfBuiltin(context_wrap(V_OUT3))

    p = PostconfBuiltin(context_wrap(V_OUT2))
    assert p['smtpd_tls_loglevel'] == '0'
    assert p['smtpd_tls_mandatory_ciphers'] == 'medium'
    assert p['smtpd_tls_mandatory_exclude_ciphers'] == ''
    assert p['smtpd_tls_mandatory_protocols'] == '!SSLv2, !SSLv3, !TLSv1'


def test_Postconf():
    with pytest.raises(SkipComponent):
        Postconf(context_wrap(V_OUT1))

    with pytest.raises(ContentException):
        Postconf(context_wrap(V_OUT3))

    p = Postconf(context_wrap(V_OUT2))
    assert p['smtpd_tls_loglevel'] == '0'
    assert p['smtpd_tls_mandatory_ciphers'] == 'medium'
    assert p['smtpd_tls_mandatory_exclude_ciphers'] == ''
    assert p['smtpd_tls_mandatory_protocols'] == '!SSLv2, !SSLv3, !TLSv1'


def test_empty():
    with pytest.raises(SkipComponent):
        PostconfBuiltin(context_wrap(""))
    with pytest.raises(SkipComponent):
        Postconf(context_wrap(""))


def test_invalid():
    with pytest.raises(SkipComponent):
        PostconfBuiltin(context_wrap("asdf"))
    with pytest.raises(SkipComponent):
        Postconf(context_wrap("asdf"))


def test_doc_examples():
    env = {
        'postconfb': PostconfBuiltin(context_wrap(V_OUT2)),
        'postconf': Postconf(context_wrap(V_OUT2)),
        '_postconf': _Postconf(context_wrap(V_OUT2)),
    }
    failed, total = doctest.testmod(postconf, globs=env)
    assert failed == 0

    # TODO
    # env = {
    #     'postconf': Postconf(context_wrap(V_OUT2)),
    # }
    # failed, total = doctest.testmod(postconf, globs=env)
    # assert failed == 0
