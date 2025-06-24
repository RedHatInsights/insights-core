import pytest

from mock.mock import patch

from insights.components.rhel_version import IsRhel6, IsRhel7
from insights.combiners.redhat_release import RedHatRelease
from insights.core.exceptions import SkipComponent
from insights.specs.datasources.corosync import corosync_cmapctl_cmds

COROSYNC_CMD_RHEL7 = [
    "/usr/sbin/corosync-cmapctl",
    "/usr/sbin/corosync-cmapctl -d runtime.schedmiss.timestamp",
    "/usr/sbin/corosync-cmapctl -d runtime.schedmiss.delay"
]

COROSYNC_CMD_RHEL9 = [
    "/usr/sbin/corosync-cmapctl",
    "/usr/sbin/corosync-cmapctl -m stats",
    "/usr/sbin/corosync-cmapctl -C schedmiss"
]


@patch('insights.specs.datasources.corosync.os.path.exists')
def test_corosync_cmapctl_cmds(path_exists):
    path_exists.return_value = True
    broker = {IsRhel6: True}
    with pytest.raises(SkipComponent):
        corosync_cmapctl_cmds(broker)

    broker = {IsRhel7: True}
    result = corosync_cmapctl_cmds(broker)
    assert result == COROSYNC_CMD_RHEL7

    broker = {RedHatRelease: True}
    result = corosync_cmapctl_cmds(broker)
    assert result == COROSYNC_CMD_RHEL9


@patch('insights.specs.datasources.corosync.os.path.exists')
def test_corosync_cmapctl_cmds_no_such_cmd(path_exists):
    path_exists.return_value = False
    broker = {IsRhel7: True}
    with pytest.raises(SkipComponent):
        corosync_cmapctl_cmds(broker)

    broker = {RedHatRelease: True}
    with pytest.raises(SkipComponent):
        corosync_cmapctl_cmds(broker)
