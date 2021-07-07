"""
Custom datasources for ps information
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by ps datasources """

    ps_eo_args = simple_command("/bin/ps -eo pid,args")
    """ Returns ps output including pid and full args """


@datasource(LocalSpecs.ps_eo_args, HostContext)
def ps_eo_cmd(broker):
    """
    Custom datasource to collect the full paths to all running commands on the system
    provided by the ``ps -eo pid,args`` command.  After collecting the data, all of the
    args are trimmed to leave only the command including full path.

    Sample output from the ``ps -eo pid, args`` command::

        PID COMMAND
          1 /usr/lib/systemd/systemd --switched-root --system --deserialize 31
          2 [kthreadd]
          3 [rcu_gp]
          4 [rcu_par_gp]
          6 [kworker/0:0H-events_highpri]
          9 [mm_percpu_wq]
         10 [rcu_tasks_kthre]
         11 /usr/bin/python3 /home/user1/python_app.py
         12 [kworker/u16:0-kcryptd/253:0]

    This datasource trims off the args to minimize possible PII and sensitive information.
    After trimming the data looks like this::

        PID COMMAND
          1 /usr/lib/systemd/systemd
          2 [kthreadd]
          3 [rcu_gp]
          4 [rcu_par_gp]
          6 [kworker/0:0H-events_highpri]
          9 [mm_percpu_wq]
         10 [rcu_tasks_kthre]
         11 /usr/bin/python3
         12 [kworker/u16:0-kcryptd/253:0]

    Returns:
        str: Returns a multiline string in the same format as ``ps`` output

    Raises:
        SkipComponent: Raised if no data is available
    """
    content = broker[LocalSpecs.ps_eo_args].content
    data = []
    data.append('PID COMMAND')
    start = False
    for l in content:
        if 'PID' in l and 'COMMAND' in l:
            start = True
            continue
        if not start:
            continue
        pid, args = l.strip().split(None, 1)
        if ' ' in args:
            cmd, _ = args.split(None, 1)
        else:
            cmd = args
        data.append('{0} {1}'.format(pid, cmd))

    if len(data) > 1:
        return DatasourceProvider('\n'.join(data), relative_path='insights_commands/ps_eo_cmd')

    raise SkipComponent()
