import os

from insights.core.dr import SkipComponent


def cmapctl_cmd_list(broker, IsRhel7, IsRhel8):
    """
    corosync-cmapctl add different arguments on RHEL7 and RHEL8.

    Returns:
        list: A list of related corosync-cmapctl commands based the RHEL version.
    """
    corosync_cmd = '/usr/sbin/corosync-cmapctl'
    if os.path.exists(corosync_cmd):
        if broker.get(IsRhel7):
            return [
                corosync_cmd,
                ' '.join([corosync_cmd, '-d runtime.schedmiss.timestamp']),
                ' '.join([corosync_cmd, '-d runtime.schedmiss.delay'])]
        if broker.get(IsRhel8):
            return [
                corosync_cmd,
                ' '.join([corosync_cmd, '-m stats']),
                ' '.join([corosync_cmd, '-C schedmiss'])]

    raise SkipComponent()
