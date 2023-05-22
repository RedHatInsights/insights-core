import doctest

from insights.parsers import systemctl_status_all
from insights.parsers.systemctl_status_all import SystemctlStatusAll
from insights.tests import context_wrap

SYSTEMCTLSTATUSALL = """
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


def test_systemctl_status():
    ret = SystemctlStatusAll(context_wrap(SYSTEMCTLSTATUSALL))
    assert "Automount point already active?" in ret
    assert ret.state == 'degraded'
    assert ret.jobs == '0 queued'
    assert ret.failed == '2 units'


def test_doc_example():
    failed_count, tests = doctest.testmod(
        systemctl_status_all,
        globs={'systemctl_status': SystemctlStatusAll(context_wrap(SYSTEMCTLSTATUSALL))}
    )
    assert failed_count == 0
