"""
Custom datasources related to ``corosync``
"""
import os
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.components.rhel_version import IsRhel7, IsRhel8, IsRhel9


@datasource(HostContext, [IsRhel7, IsRhel8, IsRhel9])
def corosync_cmapctl_cmds(broker):
    """
    corosync-cmapctl use different arguments on RHEL7 and RHEL8.

    Returns:
        list: A list of related corosync-cmapctl commands based the RHEL version.
    """
    corosync_cmd = '/usr/sbin/corosync-cmapctl'
    if os.path.exists(corosync_cmd):
        print(broker, broker.get(IsRhel7))
        # RHEL 7
        if broker.get(IsRhel7):
            return [
                corosync_cmd,
                ' '.join([corosync_cmd, '-d runtime.schedmiss.timestamp']),
                ' '.join([corosync_cmd, '-d runtime.schedmiss.delay'])]
        # Others
        elif broker.get(IsRhel8) or broker.get(IsRhel9):
            return [
                corosync_cmd,
                ' '.join([corosync_cmd, '-m stats']),
                ' '.join([corosync_cmd, '-C schedmiss'])]

    raise SkipComponent()
