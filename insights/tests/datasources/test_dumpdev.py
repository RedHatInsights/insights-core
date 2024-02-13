import pytest

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.dumpdev import dumpdev_list
from insights.parsers.mount import ProcMounts
from insights.tests import context_wrap


MOUNT = """
/dev/mapper/root / ext4 rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/httpd1 /httpd1 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
/dev/mapper/httpd2 /httpd2 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
""".strip()


MOUNT_NO_EXT = """
/dev/mapper/root / xfs rw,relatime,barrier=1,data=ordered 0 0
/dev/mapper/httpd1 /httpd1 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
/dev/mapper/httpd2 /httpd2 nfs4 rw,relatime,vers=4,barrier=1,data=ordered 0 0
""".strip()


def test_dumpdev_list():
    broker = {ProcMounts: ProcMounts(context_wrap(MOUNT))}
    result = dumpdev_list(broker)
    assert len(result) == 1
    assert '/dev/mapper/root' in result


def test_dumpdev_list_no_ext_filesystem():
    broker = {ProcMounts: ProcMounts(context_wrap(MOUNT_NO_EXT))}
    with pytest.raises(SkipComponent):
        dumpdev_list(broker)
