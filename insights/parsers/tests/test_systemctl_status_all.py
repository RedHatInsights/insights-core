import doctest

from insights.parsers import systemctl_status_all
from insights.parsers.systemctl_status_all import SystemctlStatusAll
from insights.tests import context_wrap

SYSTEMCTLSTATUSALL_ERROR_LOG = """
* redhat.test.com
    State: degraded
     Jobs: 0 queued
   Failed: 2 units
    Since: Thu 2021-09-23 12:03:43 UTC; 3h 7min ago
   CGroup: /
           |-user.slice
           | `-user-1000.slice
           |   |-user@1000.service

* proc-sys-fs-binfmt_misc.automount - Arbitrary Executable File Formats File System Automount Point
   Loaded: loaded (/usr/lib/systemd/system/proc-sys-fs-binfmt_misc.automount; static; vendor preset: disabled)
   Active: active (running) since Thu 2021-09-23 12:03:43 UTC; 3h 7min ago
    Where: /proc/sys/fs/binfmt_misc
     Docs: https://www.kernel.org/doc/html/latest/admin-guide/binfmt-misc.html
           https://www.freedesktop.org/wiki/Software/systemd/APIFileSystems

Sep 23 15:11:07 redhat.test.com systemd[1]: proc-sys-fs-binfmt_misc.automount: Automount point already active?
Sep 23 15:11:07 redhat.test.com systemd[1]: proc-sys-fs-binfmt_misc.automount: Got automount request for /proc/sys/fs/binfmt_mis
""".strip()


def test_error_log():
    log = SystemctlStatusAll(context_wrap(SYSTEMCTLSTATUSALL_ERROR_LOG))
    assert 19 == len(log.lines)
    assert "Automount point already active?" in log


def test_crio_conf_documentation():
    failed_count, tests = doctest.testmod(
        systemctl_status_all,
        globs={'log': SystemctlStatusAll(context_wrap(SYSTEMCTLSTATUSALL_ERROR_LOG))}
    )
    assert failed_count == 0
