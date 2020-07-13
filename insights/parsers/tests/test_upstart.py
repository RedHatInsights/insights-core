import doctest
import pytest
from insights.parsers import upstart, SkipException
from insights.parsers.upstart import UPstart
from insights.tests import context_wrap


INITCTL_LIST = """
rc stop/waiting
vmware-tools start/running
tty (/dev/tty3) start/running, process 9499
tty (/dev/tty2) start/running, process 9495
tty (/dev/tty1) start/running, process 9493
tty (/dev/tty6) start/running, process 9507
tty (/dev/tty5) start/running, process 9505
tty (/dev/ttyS0) start/running, process 9509
tty (/dev/tty4) stop/waiting
plymouth-shutdown stop/waiting
control-alt-delete stop/waiting
rcS-emergency stop/waiting
readahead-collector stop/waiting
kexec-disable stop/waiting
quit-plymouth stop/waiting
rcS stop/waiting
prefdm stop/waiting
init-system-dbus stop/waiting
ck-log-system-restart stop/waiting
readahead stop/waiting
ck-log-system-start stop/waiting
splash-manager stop/waiting
start-ttys stop/waiting
readahead-disable-services stop/waiting
ck-log-system-stop stop/waiting
rcS-sulogin stop/waiting
serial stop/waiting
""".strip()


def test_upstart():
    upstart_obj = UPstart(context_wrap(INITCTL_LIST))
    assert upstart_obj.upstart_managed('vmware-tools') == 'vmware-tools start/running'
    assert upstart_obj.daemon_status('vmware-tools') == 'start/running'
    assert upstart_obj.dev_status('/dev/tty6') == 'start/running'
    assert upstart_obj.tty['/dev/tty6']['status'] == 'start/running'
    assert upstart_obj.tty['/dev/tty6']['process'] == '9507'
    assert upstart_obj.tty['/dev/tty4']['status'] == 'stop/waiting'

