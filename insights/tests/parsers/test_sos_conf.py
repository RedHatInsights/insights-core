import doctest

from insights.parsers import sos_conf
from insights.tests import context_wrap

CLIENT_CONF = """
[general]
batch = yes

[plugins]
disable = rpm, selinux, dovecot

[tunables]
""".strip()


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        sos_conf,
        globs={'sos_conf': sos_conf.SosConf(context_wrap(CLIENT_CONF))}
    )
    assert failed_count == 0


def test_sos_conf():
    conf = sos_conf.SosConf(context_wrap(CLIENT_CONF))
    assert conf is not None
    sections = list(conf.sections())
    assert len(sections) == 3
    assert 'tunables' in sections
    assert conf.has_option('general', 'batch')
    assert not conf.has_option('tunables', 'rpmva')
    assert conf.get('plugins', 'disable') == 'rpm, selinux, dovecot'
    assert conf.getboolean('general', 'batch')
