import pytest
import doctest

from insights.tests import context_wrap
from insights.parsers import kpatch_list, SkipException

NORMAL_OUTPUT = '''
Loaded patch modules:
kpatch_3_10_0_1062_1_1_1_4 [enabled]

Installed patch modules:
kpatch_3_10_0_1062_1_1_1_4 (3.10.0-1062.1.1.el7.x86_64)
'''.strip()

EMPTY_OUTPUT = '''
Loaded patch modules:

Installed patch modules:
'''.strip()

BAD_OUTPUT = ''


def test_doc_examples():
    env = {
        'kpatchs': kpatch_list.KpatchList(
            context_wrap(NORMAL_OUTPUT)),
    }
    failed, total = doctest.testmod(kpatch_list, globs=env)
    assert failed == 0


def test_kpatch_list():
    kpatchs = kpatch_list.KpatchList(context_wrap(NORMAL_OUTPUT))
    assert len(kpatchs.loaded) > 0
    assert len(kpatchs.installed) > 0
    assert kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_4') == "enabled"
    assert kpatchs.installed.get('kpatch_3_10_0_1062_1_1_1_4') == "3.10.0-1062.1.1.el7.x86_64"

    kpatchs = kpatch_list.KpatchList(context_wrap(EMPTY_OUTPUT))
    assert len(kpatchs.loaded) == 0
    assert len(kpatchs.installed) == 0
    assert kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_4') is None
    assert kpatchs.installed.get('kpatch_3_10_0_1062_1_1_1_4') is None


def test_fail():
    with pytest.raises(SkipException) as e:
        kpatch_list.KpatchList(context_wrap(BAD_OUTPUT))
    assert "No Data from command: /usr/sbin/kpatch list" in str(e)
