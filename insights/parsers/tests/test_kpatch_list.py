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

MULTILINE_OUTPUT = '''
Loaded patch modules:
kpatch_3_10_0_1062_1_1_1_4 [enabled]
kpatch_3_10_0_1062_1_1_1_5 [enabled]

Installed patch modules:
kpatch_3_10_0_1062_1_1_1_4 (3.10.0-1062.1.1.el7.x86_64)
kpatch_3_10_0_1062_1_1_1_5 (3.10.0-1062.1.2.el7.x86_64)
'''.strip()

BAD_OUTPUT1 = ''

BAD_OUTPUT2 = '''
Loaded patch modules:
kpatch_3_10_0_1062_1_1_1_4 [enabled]
kpatch_3_10_0_1062_1_1_1_5

Installed patch modules:
kpatch_3_10_0_1062_1_1_1_4 (3.10.0-1062.1.1.el7.x86_64)
(3.10.0-1062.1.2.el7.x86_64)
'''.strip()


def test_doc_examples():
    env = {
        'kpatchs': kpatch_list.KpatchList(
            context_wrap(NORMAL_OUTPUT)),
    }
    failed, total = doctest.testmod(kpatch_list, globs=env)
    assert failed == 0


def test_kpatch_list():
    kpatchs = kpatch_list.KpatchList(context_wrap(MULTILINE_OUTPUT))
    assert len(kpatchs.loaded) > 0
    assert len(kpatchs.installed) > 0
    assert kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_4') == "enabled"
    assert kpatchs.installed.get('kpatch_3_10_0_1062_1_1_1_4') == "3.10.0-1062.1.1.el7.x86_64"
    assert kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_5') == "enabled"
    assert kpatchs.installed.get('kpatch_3_10_0_1062_1_1_1_5') == "3.10.0-1062.1.2.el7.x86_64"

    kpatchs = kpatch_list.KpatchList(context_wrap(BAD_OUTPUT2))
    assert len(kpatchs.loaded) == 2
    assert len(kpatchs.installed) == 1
    assert kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_4') == "enabled"
    assert kpatchs.installed.get('kpatch_3_10_0_1062_1_1_1_4') == "3.10.0-1062.1.1.el7.x86_64"
    assert kpatchs.loaded.get('kpatch_3_10_0_1062_1_1_1_5') == ''


def test_fail():
    with pytest.raises(SkipException) as e:
        kpatch_list.KpatchList(context_wrap(BAD_OUTPUT1))
    assert "No Data from command: /usr/sbin/kpatch list" in str(e)
