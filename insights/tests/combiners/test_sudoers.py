import pytest
import doctest
from insights.parsers.sudoers import EtcSudoers
from insights.combiners.sudoers import Sudoers
from insights.combiners import sudoers
from insights.tests import context_wrap

SUDOERS = """
## Allows people in group wheel to run all commands
%wheel  ALL=(ALL)       ALL
## Read drop-in files from /etc/sudoers.d (the # here does not mean a comment)
#includedir /etc/sudoers.d
""".strip()
SUDOERS_NO_INCLUDE = """
## Allows people in group wheel to run all commands
%wheel  ALL=(ALL)       ALL
## Read drop-in files from /etc/sudoers.d (the # here does not mean a comment)
##includedir /etc/sudoers.d
""".strip()
SUDOERS_FM = """
foreman-proxy ALL = (root) NOPASSWD : /opt/puppetlabs/bin/puppet cert *
Defaults:foreman-proxy !requiretty
""".strip()
SUDOERS_WH = """
%wheel  ALL=(ALL)       ABC
Defaults:wheel !requiretty
""".strip()
SUDOERS_PATH1 = "/etc/sudoers"
SUDOERS_PATH2 = "/etc/sudoers.d/forman-proxy"
SUDOERS_PATH3 = "/etc/sudoers.d/test"


def test_sudoers():
    sudo1 = EtcSudoers(context_wrap(SUDOERS, path=SUDOERS_PATH1))
    sudo2 = EtcSudoers(context_wrap(SUDOERS_FM, path=SUDOERS_PATH2))
    sudo3 = EtcSudoers(context_wrap(SUDOERS_WH, path=SUDOERS_PATH3))
    sudo = Sudoers([sudo1, sudo2, sudo3])
    assert len(sudo.lines) == 6
    assert sudo.last("#includedir") == '#includedir /etc/sudoers.d'
    assert len(sudo.get(['wheel', 'includedir'])) == 0
    assert len(sudo.get(['wheel', 'includedir'], check=any)) == 4
    assert sudo.last(['Defaults', 'includedir'], check=all) is None
    assert len(sudo.get(['foreman-proxy', 'NOPASSWD'], check=all)) == 1
    assert len(sudo.get(['foreman-proxy', 'NOPASSWD'], check=any)) == 2
    wheel = sudo.get(['wheel', 'ALL=(ALL)'])
    assert len(wheel) == 2
    assert wheel[1] == '%wheel  ALL=(ALL)       ABC'
    assert sudo.last("Defaults") == 'Defaults:wheel !requiretty'

    assert sudo.data['/etc/sudoers'] == ['%wheel  ALL=(ALL)       ALL', '#includedir /etc/sudoers.d']
    assert sudo.data['/etc/sudoers.d/test'] == ['%wheel  ALL=(ALL)       ABC', 'Defaults:wheel !requiretty']

    with pytest.raises(TypeError):
        sudo.get({})


def test_sudoers_no_includedir():
    sudo1 = EtcSudoers(context_wrap(SUDOERS_NO_INCLUDE, path=SUDOERS_PATH1))
    sudo2 = EtcSudoers(context_wrap(SUDOERS_FM, path=SUDOERS_PATH2))
    sudo3 = EtcSudoers(context_wrap(SUDOERS_WH, path=SUDOERS_PATH3))
    sudo = Sudoers([sudo1, sudo2, sudo3])
    assert sudo.data['/etc/sudoers'] == ['%wheel  ALL=(ALL)       ALL']
    assert len(sudo.lines) == 1


def test_doc_examples():
    sudo1 = EtcSudoers(context_wrap(SUDOERS, path=SUDOERS_PATH1))
    sudo2 = EtcSudoers(context_wrap(SUDOERS_FM, path=SUDOERS_PATH2))
    env = {
        'sudo': Sudoers([sudo1, sudo2])
    }
    failed, total = doctest.testmod(sudoers, globs=env)
    assert failed == 0
