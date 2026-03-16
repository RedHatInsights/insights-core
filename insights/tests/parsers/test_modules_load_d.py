import doctest

from insights.parsers import modules_load_d
from insights.parsers.modules_load_d import ModulesLoadD
from insights.tests import context_wrap

CIFS_CONTENT = """
cifs
""".strip()


def test_modules_load_d():
    modules = ModulesLoadD(context_wrap(CIFS_CONTENT, path='/etc/modules-load.d/cifs.conf'))

    assert len(modules) == 1
    assert 'cifs.conf' in modules
    assert modules['cifs.conf'] == CIFS_CONTENT


def test_doc_examples():
    env = {
        'modules_load': modules_load_d.ModulesLoadD(context_wrap(CIFS_CONTENT, path='/etc/modules-load.d/cifs.conf')),
    }
    failed, _ = doctest.testmod(modules_load_d, globs=env)
    assert failed == 0
