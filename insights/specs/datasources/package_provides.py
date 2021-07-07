"""
Custom datasource for package_provides
"""
import logging
import signal

from insights.combiners.ps import Ps
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.filters import get_filters
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider
from insights.specs import Specs

from . import get_running_commands, DEFAULT_SHELL_TIMEOUT

logger = logging.getLogger(__name__)


def get_package(ctx, file_path):
    """
    Get the RPM package that owns the specified filename with path

    Arguments:
        ctx: The current execution context
        file_path(str): The full path and filename for RPM query

    Returns:
        str: The name of the RPM package that provides the ``file``
        or None if file is not associated with an RPM.
    """
    rc, resolved = ctx.shell_out(
        "/usr/bin/readlink -e {0}".format(file_path),
        timeout=DEFAULT_SHELL_TIMEOUT,
        keep_rc=True
    )
    if rc == 0 and resolved:
        rc, pkg = ctx.shell_out(
            "/usr/bin/rpm -qf {0}".format(resolved[0]),
            timeout=DEFAULT_SHELL_TIMEOUT,
            keep_rc=True,
            signum=signal.SIGTERM
        )
        if rc == 0 and pkg:
            return pkg[0]


@datasource(Ps, HostContext)
def cmd_and_pkg(broker):
    """
    Collect a list of running commands and the associated RPM package providing those commands.
    The commands are based on filters so rules must add the desired commands as filters to
    enable collection.  If a command is not provided by an RPM then it will not be included
    in the output.

    In order for the full command line to be present in the Ps combiner a filter must be added
    to the spec ``ps_auxww``.  A filter must also be added to ``package_provides_command`` so
    this datasource will look for the command in Ps.

    Arguments:
        broker: the broker object for the current session

    Returns:
        DatasourceProvider: Returns the collected information as a file with 1 line per command

    Raises:
        SkipComponent: Raised if no data is collected
    """
    commands = get_filters(Specs.package_provides_command)
    """ list: List of commands to search for, added as filters for the spec """

    if commands:
        pkg_cmd = list()
        for cmd in get_running_commands(broker[Ps], broker[HostContext], list(commands)):
            pkg = get_package(broker[HostContext], cmd)
            if pkg is not None:
                pkg_cmd.append("{0} {1}".format(cmd, pkg))
        if pkg_cmd:
            return DatasourceProvider('\n'.join(pkg_cmd), relative_path='insights_commands/package_provides_command')
    raise SkipComponent
