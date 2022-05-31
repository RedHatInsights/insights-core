"""
Custom datasources related to ``httpd``
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.combiners.ps import Ps
from insights.specs.datasources import get_running_commands


@datasource(Ps, HostContext)
def httpd_cmds(broker):
    """
    Function to search the output of ``ps auxcww`` to find all running Apache
    webserver processes and extract the binary path.

    Returns:
        list: List of the binary paths to each running process
    """
    cmds = get_running_commands(broker[Ps], broker[HostContext], ['httpd', ])
    if cmds:
        return cmds
    raise SkipComponent
