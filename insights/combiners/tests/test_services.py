from ...parsers.chkconfig import ChkConfig
from ...parsers.systemd.unitfiles import UnitFiles
from ..services import Services
from ...tests import context_wrap

CHKCONIFG = """
auditd         	0:off	1:off	2:on	3:on	4:on	5:on	6:off
crond          	0:off	1:off	2:on	3:on	4:on	5:on	6:off
iptables       	0:off	1:off	2:on	3:on	4:on	5:on	6:off
kdump          	0:off	1:off	2:off	3:on	4:on	5:on	6:off
restorecond    	0:off	1:off	2:off	3:off	4:off	5:off	6:off
""".strip()

# Worth noting that actual systemctl list-unit-files output has spaces on
# the ends, but we strip them.
SYSTEMCTL = """
UNIT FILE                                   STATE
auditd.service                              enabled
cpupower.service                            disabled
crond.service                               enabled
emergency.service                           static
firewalld.service                           enabled
fstrim.service                              static
kdump.service                               enabled

7 unit files listed.
""".strip()


def test_chkconfig():
    context = context_wrap(CHKCONIFG)
    chkconfig = ChkConfig(context)
    services = Services(chkconfig, None)
    assert len(services.services) == 5
    assert len(services.parsed_lines) == 5
    assert services.is_on('auditd')
    assert services.is_on('crond')
    assert not services.is_on('restorecond')
    assert not services.is_on('ksm')
    assert services.service_line('auditd') == "auditd         	0:off	1:off	2:on	3:on	4:on	5:on	6:off"
    assert services.service_line('ksm') == ''
    # Test __contains__ functionality
    assert 'crond' in services
    assert 'ksm' not in services


def test_systemctl():
    context = context_wrap(SYSTEMCTL)
    unitfiles = UnitFiles(context)
    services = Services(None, unitfiles)
    assert len(services.services) == 7
    assert len(services.parsed_lines) == 7
    assert services.is_on('auditd.service')
    assert services.is_on('crond.service')
    assert not services.is_on('cpupower.service')
    assert services.is_on('auditd')
    assert services.is_on('crond')
    assert not services.is_on('cpupower')
    assert not services.is_on('ksm')
    assert not services.is_on('ksm.service')
    assert services.service_line('auditd.service') == "auditd.service                              enabled"
    # Test __contains__ functionality
    assert 'crond' in services
    assert 'ksm' not in services


def test_combined():
    context = context_wrap(CHKCONIFG)
    chkconfig = ChkConfig(context)
    context = context_wrap(SYSTEMCTL)
    unitfiles = UnitFiles(context)
    services = Services(chkconfig, unitfiles)
    assert len(services.services) == 12
    assert len(services.parsed_lines) == 12
    assert services.is_on('auditd')
    assert services.is_on('crond')
    assert not services.is_on('restorecond')
    assert services.is_on('auditd.service')
    assert services.is_on('crond.service')
    assert not services.is_on('cpupower.service')
    assert not services.is_on('cpupower')
    # Test __contains__ functionality
    assert 'crond' in services
    assert 'ksm' not in services
