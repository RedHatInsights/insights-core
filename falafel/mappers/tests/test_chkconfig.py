from ...tests import context_wrap
from ..chkconfig import ChkConfig

SERVICES = """
auditd         	0:off	1:off	2:on	3:on	4:on	5:on	6:off
crond          	0:off	1:off	2:on	3:on	4:on	5:on	6:off
iptables       	0:off	1:off	2:on	3:on	4:on	5:on	6:off
kdump          	0:off	1:off	2:off	3:on	4:on	5:on	6:off
restorecond    	0:off	1:off	2:off	3:off	4:off	5:off	6:off
""".strip()

ERROR = """
-bash: chkconfig: command not found
"""


def test_chkconfig():
    context = context_wrap(SERVICES)
    chkconfig = ChkConfig(context)
    assert len(chkconfig.services) == 5
    assert len(chkconfig.parsed_lines) == 5
    assert chkconfig.is_on('crond')
    assert chkconfig.is_on('kdump')
    assert not chkconfig.is_on('restorecond')


def test_command_not_found():
    context = context_wrap(ERROR)
    chkconfig = ChkConfig(context)
    assert len(chkconfig.services) == 0
    assert len(chkconfig.parsed_lines) == 0
    assert not chkconfig.is_on('crond')
    assert not chkconfig.is_on('kdump')
    assert not chkconfig.is_on('restorecond')
