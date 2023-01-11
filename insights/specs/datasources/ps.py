"""
Custom datasources for ps information
"""
import json
import os.path

from insights.core.context import HostContext
from insights.core.exceptions import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_command
from insights.specs import Specs


class LocalSpecs(Specs):
    """ Local specs used only by ps datasources """

    ps_eo_args = simple_command("/bin/ps -ewwo pid,args")
    """ Returns ps output including pid and full args """


@datasource(LocalSpecs.ps_eo_args, HostContext)
def ps_eo_cmd(broker):
    """
    Custom datasource to collect the full paths to all running commands on the system
    provided by the ``ps -ewwo pid,args`` command.  After collecting the data, all of the
    args are trimmed to leave only the command including full path.

    Sample output from the ``ps -ewwo pid, args`` command::

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


@datasource(LocalSpecs.ps_eo_args, HostContext)
def jboss_runtime_versions(broker):
    """
     Custom datasource to collect the <JBOSS_HOME>/version.txt.

     Sample output from the ``ps -ewwo pid, args`` command::

         PID COMMAND
           1 /usr/lib/systemd/systemd --switched-root --system --deserialize 31
           2 [kthreadd]
           3 [rcu_gp]
           4 [rcu_par_gp]
           6 [kworker/0:0H-events_highpri]
           8686 java -D[Standalone] -server -verbose:gc -Xms64m -Xmx512m -Djboss.home.dir=/opt/jboss-datagrid-7.3.0-server -Djboss.server.base.dir=/opt/jboss-datagrid-7.3.0-server/standalone


     Get the Jboss home directory and read the version.txt::

         -Djboss.home.dir=/opt/jboss-datagrid-7.3.0-server
         /opt/jboss-datagrid-7.3.0-server/version.txt

     Returns:
         str: string of dict {<jboss_home>: <content of version.txt>}

     Raises:
         SkipComponent: Raised if no data is available
     """
    content = broker[LocalSpecs.ps_eo_args].content
    jboss_home_dirs = set()
    data = {}
    for l in content:
        if 'java ' in l:
            jboss_home_labels = ['-jboss-home ', '-Djboss.home.dir=', '-Dcatalina.home=',
                                 '-Dinfinispan.server.home.path=']
            for jhl in jboss_home_labels:
                if jhl in l:
                    jboss_home_str = l.split(jhl)[1]
                    if jboss_home_str.startswith('/'):
                        jboss_home_dirs.add(jboss_home_str.split()[0])
    if jboss_home_dirs:
        for one_jboss_home_dir in jboss_home_dirs:
            jboss_v_file = os.path.join(one_jboss_home_dir, 'version.txt')
            if os.path.exists(jboss_v_file):
                with open(jboss_v_file, 'r') as version_file:
                    data[one_jboss_home_dir] = version_file.read()
    if len(data) > 0:
        return DatasourceProvider(json.dumps(data), relative_path='insights_commands/jboss_versions')
    raise SkipComponent()
