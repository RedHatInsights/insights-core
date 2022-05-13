import doctest
from insights.parsers import dnf_modules
from insights.tests import context_wrap

DNF_MODULES_INPUT = """
[postgresql]
name=postgresql
profiles=client
state=enabled
stream=9.6
[python36]
name=python36
profiles=
state=enabled
stream=3.6
[virt]
name=virt
profiles=
state=enabled
stream=rhel
"""


def test_dnf_modules():
    modules_config = dnf_modules.DnfModules(context_wrap(DNF_MODULES_INPUT))
    assert modules_config is not None
    assert 'postgresql' in modules_config.sections()
    assert 'python36' in modules_config.sections()
    assert 'virt' in modules_config.sections()
    assert 'enabled' == modules_config.get('postgresql', 'state')


def test_dnf_modules_doc_examples():
    failed, total = doctest.testmod(
        dnf_modules,
        globs={'dnf_modules': dnf_modules.DnfModules(context_wrap(DNF_MODULES_INPUT))}
    )
    assert failed == 0
