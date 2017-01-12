import pytest
from ...tests import context_wrap
from ..chkconfig import ChkConfig

SERVICES = """
auditd         	0:off	1:off	2:on	3:on	4:on	5:on	6:off
crond          	0:off	1:off	2:on	3:on	4:on	5:on	6:off
iptables       	0:off	1:off	2:on	3:on	4:on	5:on	6:off
kdump          	0:off	1:off	2:off	3:on	4:on	5:on	6:off
restorecond    	0:off	1:off	2:off	3:off	4:off	5:off	6:off
xinetd          0:off   1:off   2:on    3:on    4:on    5:on    6:off
        rexec:          off
        rlogin:         off
        rsh:            on
        tcpmux-server:  off
        telnet:         on
""".strip()

ERROR = """
-bash: chkconfig: command not found
"""


def test_chkconfig():
    context = context_wrap(SERVICES)
    chkconfig = ChkConfig(context)
    assert len(chkconfig.services) == 11
    assert len(chkconfig.parsed_lines) == 11
    assert chkconfig.is_on('crond')
    assert chkconfig.is_on('kdump')
    assert chkconfig.is_on('telnet')
    assert not chkconfig.is_on('restorecond')
    assert not chkconfig.is_on('rlogin')


def test_command_not_found():
    context = context_wrap(ERROR)
    chkconfig = ChkConfig(context)
    assert len(chkconfig.services) == 0
    assert len(chkconfig.parsed_lines) == 0
    assert not chkconfig.is_on('crond')
    assert not chkconfig.is_on('kdump')
    assert not chkconfig.is_on('restorecond')


def test_levels_on():
    chkconfig = ChkConfig(context_wrap(SERVICES))
    assert chkconfig.levels_on('crond') == set(['2', '3', '4', '5'])
    assert chkconfig.levels_on('telnet') == set(['2', '3', '4', '5'])
    assert chkconfig.levels_on('rlogin') == set([])
    with pytest.raises(KeyError):
        assert chkconfig.levels_on('bad_name')


def test_levels_off():
    chkconfig = ChkConfig(context_wrap(SERVICES))
    assert chkconfig.levels_off('crond') == set(['0', '1', '6'])
    assert chkconfig.levels_off('telnet') == set(['0', '1', '6'])
    assert chkconfig.levels_off('rlogin') == set(['0', '1', '2', '3',
                                                    '4', '5', '6'])
    with pytest.raises(KeyError):
        assert chkconfig.levels_off('bad_name')
