import doctest

from insights.parsers.modinfo import KernelModulesInfo
from insights.combiners.modinfo import ModulesInfo
from insights.tests.parsers.test_modinfo import (
        MODINFO_I40E, MODINFO_INTEL, MODINFO_BNX2X
)
from insights.tests import context_wrap
from insights.combiners import modinfo


def test_modinfo_doc_examples():
    filter_modules = KernelModulesInfo(context_wrap(
        '{0}\n{1}\n{2}'.format(
            MODINFO_I40E,
            MODINFO_INTEL,
            MODINFO_BNX2X)
    ))
    combiner_obj = ModulesInfo(filter_modules)
    env = {'modules_obj': combiner_obj}
    failed, total = doctest.testmod(modinfo, globs=env)
    assert failed == 0


def test_modules_info():
    filter_modules = KernelModulesInfo(context_wrap(
        '{0}\n{1}\n{2}'.format(
            MODINFO_I40E,
            MODINFO_INTEL,
            MODINFO_BNX2X)
    ))
    combiner_obj = ModulesInfo(
        filter_modules
    )
    assert 'i40e' in combiner_obj
    assert combiner_obj['i40e']['signer'] == 'Red Hat Enterprise Linux kernel signing key'
    assert len(combiner_obj) == 3
    assert 'abc' not in combiner_obj
    assert 'i40e' in combiner_obj.retpoline_y
