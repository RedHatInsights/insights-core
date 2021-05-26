import signal

from insights.combiners.ps import Ps
from insights.combiners.cloud_provider import CloudProvider
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource


def get_running_commands(broker, commands):
    """
    Search for command in ``ps auxcww`` output and determine RPM providing binary

    Arguments:
        broker(dict): Current state of specs collected by Insights
        commands(str or list): Command or list of commands to search for in ps output

    Returns:
        list: List of the full command paths of the ``command``.

    Raises:
        Exception: Raises an exception if commands object is not a list or is empty
    """
    if not commands or not isinstance(commands, list):
        raise Exception('Commands argument must be a list object and contain at least one item')

    ps_list = [broker[Ps].search(COMMAND_NAME__contains=c) for c in commands]
    ps_cmds = [i for sub_l in ps_list for i in sub_l]
    ctx = broker[HostContext]

    ret = set()
    for cmd in set(p['COMMAND_NAME'] for p in ps_cmds):
        try:
            which = ctx.shell_out("/usr/bin/which {0}".format(cmd))
        except Exception:
            continue
        ret.add(which[0]) if which else None
    return sorted(ret)


def get_package(broker, command):
    """
    Arguments:
        broker(dict): Current state of specs collected by Insights
        command(str): The full command name to get the package

    Returns:
        str: The package that provides the ``command``.
    """
    ctx = broker[HostContext]
    resolved = ctx.shell_out("/usr/bin/readlink -e {0}".format(command))
    if resolved:
        pkg = ctx.shell_out("/usr/bin/rpm -qf {0}".format(resolved[0]), signum=signal.SIGTERM)
        if pkg:
            return pkg[0]
    raise SkipComponent


@datasource(CloudProvider, HostContext)
def is_aws(broker):
    """ bool: Returns True if this node is identified as running in AWS """
    cp = broker[CloudProvider]
    if cp and cp.cloud_provider == CloudProvider.AWS:
        return True
    raise SkipComponent()
