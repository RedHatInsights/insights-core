"""
Custom datasources for corosync information
"""
import os

from insights.components.rhel_version import IsRhel8, IsRhel7
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource


@datasource(HostContext, [IsRhel7, IsRhel8])
def cmapctl_cmd_list(broker):
    """
    Returns a list of commands based on ``/usr/sbin/corosync-cmapctl``

    Different args are added to each command based on the version of RHEL.

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
