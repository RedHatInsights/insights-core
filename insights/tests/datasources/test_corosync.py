import pytest

from mock.mock import patch

from insights.combiners.redhat_release import RedHatRelease
from insights.core.exceptions import SkipComponent
from insights.parsers.redhat_release import RedhatRelease
from insights.specs.datasources.corosync import corosync_cmapctl_cmds
from insights.tests import context_wrap

COROSYNC_CMD_RHEL7 = [
    "/usr/sbin/corosync-cmapctl",
    "/usr/sbin/corosync-cmapctl -d runtime.schedmiss.timestamp",
    "/usr/sbin/corosync-cmapctl -d runtime.schedmiss.delay",
]

COROSYNC_CMD_RHEL9 = [
    "/usr/sbin/corosync-cmapctl",
    "/usr/sbin/corosync-cmapctl -m stats",
    "/usr/sbin/corosync-cmapctl -C schedmiss",
]

RHEL6 = "Red Hat Enterprise Linux Server release 6.5 (Santiago)"
RHEL7 = "Red Hat Enterprise Linux Server release 7.0 (Maipo)"
RHEL9 = "Red Hat Enterprise Linux release 9.0 (Plow)"


@patch('insights.specs.datasources.corosync.os.path.exists')
def test_corosync_cmapctl_cmds(path_exists):
    path_exists.return_value = True
    rhel = RedHatRelease(None, RedhatRelease(context_wrap(RHEL6)))
    broker = {RedHatRelease: rhel}
    with pytest.raises(SkipComponent):
        corosync_cmapctl_cmds(broker)

    rhel = RedHatRelease(None, RedhatRelease(context_wrap(RHEL7)))
    broker = {RedHatRelease: rhel}
    result = corosync_cmapctl_cmds(broker)
    assert result == COROSYNC_CMD_RHEL7

    rhel = RedHatRelease(None, RedhatRelease(context_wrap(RHEL9)))
    broker = {RedHatRelease: rhel}
    result = corosync_cmapctl_cmds(broker)
    assert result == COROSYNC_CMD_RHEL9


@patch('insights.specs.datasources.corosync.os.path.exists')
def test_corosync_cmapctl_cmds_no_such_cmd(path_exists):
    path_exists.return_value = False
    rhel = RedHatRelease(None, RedhatRelease(context_wrap(RHEL7)))
    broker = {RedHatRelease: rhel}
    with pytest.raises(SkipComponent):
        corosync_cmapctl_cmds(broker)

    rhel = RedHatRelease(None, RedhatRelease(context_wrap(RHEL9)))
    broker = {RedHatRelease: rhel}
    with pytest.raises(SkipComponent):
        corosync_cmapctl_cmds(broker)
