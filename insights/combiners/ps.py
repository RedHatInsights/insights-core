"""
Ps - Combiner for ps command output
===================================

This shared combiner combines all of the information produced by the individual
`ps` parsers.

Class ``PsAuxww`` parses the output of the ``ps auxww`` command.  Similar output
for ``ps aux`` and ``ps auxcww`` A small
sample of the output of this command looks like::

    USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
    root      1661  0.0  0.0 126252  1392 ?        Ss   May31   0:04 /usr/sbin/crond -n

Class ``PsEf`` parses the output of the ``ps -ef`` command.  A small
sample of the output of this command looks like::

    UID         PID   PPID  C STIME TTY          TIME CMD
    root          1      0  0 03:53 ?        00:00:06 /usr/lib/systemd/systemd --system --deserialize 15
    root          2      0  0 03:53 ?        00:00:00 [kthreadd]
    root       1803      1  5 03:54 ?        00:55:22 /usr/bin/openshift start master --config=/etc/origin/master/master-config.yaml --loglevel

``ps -eo pid,ppid,comm sample input data::

      PID  PPID COMMAND
        1     0 systemd
        2     0 kthreadd
        3     2 ksoftirqd/0

ps -ef, ps aux, ps auxww are filtered.
"""

from insights.core.plugins import combiner
from insights.parsers.ps import PsAuxww, PsEf, PsAuxcww, PsAux, PsEo

class Process(object):

    def __init__(self, proc):
        self.process = {}
        for k, v in six.iteritems(proc):
            self.proc[k] = v

        if 'UID' in self.proc:
            self.proc['USER'] = self.proc['UID']

        if 'CMD' in self.proc:
            self.proc['COMMAND'] = self.proc['CMD']


@combiner([PsAux, PsAuxww, PsAuxcww, PsEf, PsEo])
class Ps(object):

    def __init__(self, ps_aux, ps_auxww, ps_auxcww, ps_ef, ps_eo):
        self.processes = {}
        pids = {}
        for source in [ps_aux, ps_auxww, ps_ef, ps_eo, ps_auxcww]:
            if source:
                for p in source.data:
                    if 'PID' in p:
                        if p['PID'] in pids:
                            self.processes[p['PID']].update(p)
                        else:
                            self.processes[p['PID']] = p


