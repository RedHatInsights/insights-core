"""
Custom datasources related to ``corosync``
"""
import os

from insights.components.rhel_version import IsRhel7, IsRhel6
from insights.combiners.redhat_release import RedHatRelease
from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource


@datasource(HostContext, [IsRhel6, IsRhel7, RedHatRelease])
def corosync_cmapctl_cmds(broker):
    """
    corosync-cmapctl use different arguments on RHEL7 and RHEL8.

    Returns:
        list: A list of related corosync-cmapctl commands based the RHEL version.
    """
    corosync_cmd = '/usr/sbin/corosync-cmapctl'
    if os.path.exists(corosync_cmd):
        if broker.get(IsRhel6):
            raise SkipComponent()
        elif broker.get(IsRhel7):
            return [
                corosync_cmd,
                ' '.join([corosync_cmd, '-d runtime.schedmiss.timestamp']),
                ' '.join([corosync_cmd, '-d runtime.schedmiss.delay'])]
        # Others
        else:
            return [
                corosync_cmd,
                ' '.join([corosync_cmd, '-m stats']),
                ' '.join([corosync_cmd, '-C schedmiss'])]
    raise SkipComponent()
