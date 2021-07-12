"""
Custom datasources provide functionality beyond ``simple_file`` and ``simple_command``
type datasources.  If the custom datasource is short and concise it may be added to
this module.  Other datasources should be added as a separate module.
Normally custom datasources are necessary for core-collection.  In order for a custom
datasource to execute, all of its dependencies must be explicitly loaded by the client.
The client uses the YAML template :py:data:`insights.collect.default_manifest` and each
parser/combiner/component required by a custom datasource must be included in the YAML
template to ensure it is loaded.
"""
DEFAULT_SHELL_TIMEOUT = 10
""" int: Default timeout in seconds for ctx.shell_out() commands, must be provided as an arg """


def get_running_commands(ps, ctx, commands):
    """
    Search for a list of commands in Ps combiner output and returns the full path
    to the command

    Arguments:
        ps: Ps combiner object
        ctx: Context of the current collection
        commands(list): List of commands to search for in ps output

    Returns:
        list: List of the full command paths of the all ``command``.

    Raises:
        TypeError: Raised when ``commands`` args is not a list
    """
    if not commands or not isinstance(commands, list):
        raise TypeError('Commands argument must be a list object and contain at least one item')

    ps_list = [ps.search(COMMAND_NAME__contains=c) for c in commands]
    if ps_list and isinstance(ps_list[0], list):
        ps_cmds = [i for sub_l in ps_list for i in sub_l]
    else:
        ps_cmds = ps_list

    ret = set()
    for cmd in set(p['COMMAND'] for p in ps_cmds):
        try:
            cmd_prefix = cmd.split(None, 1)[0]
            which = ctx.shell_out("/usr/bin/which {0}".format(cmd_prefix), timeout=DEFAULT_SHELL_TIMEOUT)
        except Exception:
            continue
        ret.add(which[0]) if which else None
    return sorted(ret)
