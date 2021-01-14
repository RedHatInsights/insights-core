"""
ProcEnvironAll - Combiner ``/proc/<PID>/environ``
=================================================

The Combiner combiners and wraps all the
:class:`insights.parsers.proc_environ.ProcEnviron` in to a list.

"""
from insights import add_filter
from insights.core.plugins import combiner
from insights.combiners.ps import Ps
from insights.parsers.proc_environ import ProcEnviron as PE


add_filter(Ps, 'PID')


@combiner(PE, Ps)
class ProcEnvironAll(list):
    """
    Class for parsing the ``/proc/<PID>/environ`` file into a dictionaries
    with environment variable name as key and containing environment variable
    value.

    Examples:
        >>> proc_envs[0]['REGISTRIES']
        '--add-registry registry.access.redhat.com'
        >>> proc_envs.get_environ_of_proc('openshift-route').pid
        131
    """

    def __init__(self, pe, ps):
        self.extend(pe)
        self._ps = ps

    def get_environ_of_proc(self, proc_name):
        """
        Returns the :class:`insights.parsers.proc_environ.ProcEnviron` of the
        specified `proc_name`.

        Args:
            proc_name (str): Name of the process that want to check.

        Returns:
            ProcEnviron (str): The parse result of the environ. None when no
                such `proc_name`.
        """
        proc_ps = self._ps.search(COMMAND_NAME__contains=proc_name)
        pid = proc_ps[-1]['PID'] if proc_ps else None
        if pid:
            pe = [env for env in self if env.pid == pid]
            if pe:
                return pe[0]
