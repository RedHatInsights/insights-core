import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import sudoers
from insights.parsers.sudoers import EtcSudoers
from insights.tests import context_wrap

SUDOERS = """
## Allows people in group wheel to run all commands
%wheel  ALL=(ALL)       ALL
## Read drop-in files from /etc/sudoers.d (the # here does not mean a comment)
#includedir /etc/sudoers.d
""".strip()
SUDOERS_EMPTY = ""


def test_etc_sudoers():
    sudo = EtcSudoers(context_wrap(SUDOERS))
    assert len(sudo.lines) == 2
    assert sudo.get(['wheel', 'ALL=(ALL)', 'ALL']) == ['%wheel  ALL=(ALL)       ALL']
    assert sudo.last("#includedir") == '#includedir /etc/sudoers.d'
    assert len(sudo.get(['wheel', 'includedir'])) == 0
    assert len(sudo.get(['wheel', 'includedir'], check=any)) == 2
    assert sudo.last(['wheel', 'includedir'], check=any) == '#includedir /etc/sudoers.d'


def test_ab():
    with pytest.raises(SkipComponent):
        EtcSudoers(context_wrap(SUDOERS_EMPTY))

    sudo = EtcSudoers(context_wrap(SUDOERS))
    with pytest.raises(TypeError):
        sudo.get({})


def test_doc_examples():
    env = {
        'sudo': EtcSudoers(context_wrap(SUDOERS))
    }
    failed, total = doctest.testmod(sudoers, globs=env)
    assert failed == 0
