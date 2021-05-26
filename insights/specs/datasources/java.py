from insights.combiners.ps import Ps
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource

from . import get_package, get_running_commands


@datasource(Ps, HostContext)
def cmd_and_pkg(broker):
    """
    Returns:
        list: List of the command and provider package string of the specified commands.

    Attributes:
        COMMANDS (list): List of the specified commands that need to check the provider package.
    """
    COMMANDS = ['java']
    pkg_cmd = list()
    for cmd in get_running_commands(broker, COMMANDS):
        pkg_cmd.append("{0} {1}".format(cmd, get_package(broker, cmd)))

    if pkg_cmd:
        return '\n'.join(pkg_cmd)

    raise SkipComponent()
