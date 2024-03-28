from insights.combiners import ps
from insights.combiners.ps import Ps
from insights.parsers.ps import PsAlxwww, PsAuxww, PsAux, PsAuxcww, PsEf, PsEoCmd
from insights.tests import context_wrap
import doctest

PS_EO_CMD_LINES = """
  PID  PPID NLWP COMMAND
    1     0    1 /usr/lib/systemd/systemd
    2     0    1 [kthreadd]
    3     2    1 [ksoftirqd/0]
    8     2    1 [migration/0]
    9     2    1 [rcu_bh]
   10     2    1 [rcu_sched]
   13     2    1 /usr/bin/python3.6
 """

PS_AUXCWW_LINES = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.1  0.0 195712  7756 ?        Ss    2019 477:10 systemd
root         2  0.0  0.0      0     0 ?        S     2019   1:04 kthreadd
root         3  0.0  0.0      0     0 ?        S     2019  36:41 ksoftirqd/0
root         8  0.0  0.0      0     0 ?        S     2019  31:50 migration/0
root         9  0.1  0.0      0     0 ?        S     2019   0:00 rcu_bh
root        11  0.1  0.0      0     0 ?        S     2019  05:00 watchdog/0
"""

PS_EF_LINES = """
UID        PID  PPID  C STIME TTY          TIME CMD
root         1     0  0  2019 ?        07:57:10 /usr/lib/systemd/systemd --switched-root --system --deserialize 21
root         2     0  0  2019 ?        00:01:04 [kthreadd]
root         3     2  0  2019 ?        00:36:41 [ksoftirqd/0]
root         8     2  0  2019 ?        00:31:50 [migration/0]
root         9     2  0  2019 ?        00:00:00 [rcu_bh]
root        12     2  0  2019 ?        00:05:00 [watchdog/1]
"""

PS_AUX_LINES = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.1  0.0 195712  7756 ?        Ss    2019 478:05 /usr/lib/systemd/systemd --switched-root --system --deserialize 21
root         2  0.0  0.0      0     0 ?        S     2019   1:04 [kthreadd]
root         3  0.0  0.0      0     0 ?        S     2019  36:47 [ksoftirqd/0]
root         8  0.0  0.0      0     0 ?        S     2019  32:38 [migration/0]
root         9  0.1  0.0      0     0 ?        S     2019   0:00 [rcu_bh]
"""

PS_AUXWW_LINES = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.1  0.0 195712  7756 ?        Ss    2019 478:05 /usr/lib/systemd/systemd --switched-root --system --deserialize 21
root         2  0.0  0.0      0     0 ?        S     2019   1:04 [kthreadd]
root         3  0.0  0.0      0     0 ?        S     2019  36:47 [ksoftirqd/0]
root         8  0.0  0.0      0     0 ?        S     2019  32:38 [migration/0]
root         9  0.1  0.0      0     0 ?        S     2019   0:00 [rcu_bh]
"""

PS_ALXWWW_LINES = """
F   UID   PID  PPID PRI  NI    VSZ   RSS WCHAN  STAT TTY        TIME COMMAND
4     0     1     0  20   0 195712  7756 ep_pol Ss   ?        478:05 /usr/lib/systemd/systemd --switched-root --system --deserialize 21
1     0     2     0  20   0      0     0 kthrea S    ?          1:04 [kthreadd]
1     0     3     2  20   0      0     0 smpboo S    ?         36:47 [ksoftirqd/0]
1     0     8     2 -100  -      0     0 smpboo S    ?         32:38 [migration/0]
1     0     9     2  20   0      0     0 rcu_gp S    ?          0:00 [rcu_bh]
"""

PS_AUXWWWM_LINES = """
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           1  1.8  0.8  24228 15660 ?        -    09:56   0:00 /usr/lib/systemd/systemd rhgb --switched-root --system --deserialize 31
root           -  1.8    -      -     - -        Ss   09:56   0:00 -
root           2  0.0  0.0      0     0 ?        -    09:56   0:00 [kthreadd]
root           -  0.0    -      -     - -        S    09:56   0:00 -
root           3  0.0  0.0      0     0 ?        -    09:56   0:00 [rcu_gp]
root           -  0.0    -      -     - -        I<   09:56   0:00 -
root           4  0.0  0.0      0     0 ?        -    09:56   0:00 [rcu_par_gp]
root           -  0.0    -      -     - -        I<   09:56   0:00 -
"""


def test_psauxcww_parser():
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps = Ps(None, None, None, None, ps_auxcww, None)
    assert len(ps.processes) == 6
    proc9 = ps[9]
    assert proc9['USER'] == 'root'
    assert proc9['TTY'] == '?'
    assert proc9['%CPU'] == 0.1
    assert proc9['%MEM'] == 0.0
    assert proc9['COMMAND'] == proc9['COMMAND_NAME']


def test_pseocmd_parser():
    ps_eo_cmd = PsEoCmd(context_wrap(PS_EO_CMD_LINES, strip=False))
    ps = Ps(None, None, None, None, None, ps_eo_cmd)
    assert len(ps.processes) == 7
    proc = ps[1]
    assert proc['USER'] is None
    assert proc['TTY'] is None
    assert proc['%CPU'] is None
    assert proc['%MEM'] is None
    assert proc['COMMAND'] == '/usr/lib/systemd/systemd'
    assert proc['COMMAND_NAME'] == 'systemd'
    assert proc['PPID'] == 0
    assert proc['NLWP'] == '1'


def test_psauxcww_and_pseocmd_parsers():
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps_eo_cmd = PsEoCmd(context_wrap(PS_EO_CMD_LINES, strip=False))
    ps = Ps(None, None, None, None, ps_auxcww, ps_eo_cmd)
    assert len(ps.processes) == 8
    proc9 = ps[9]
    assert proc9['USER'] == 'root'
    assert proc9['TTY'] == '?'
    assert proc9['%CPU'] == 0.1
    assert proc9['%MEM'] == 0.0
    assert proc9['COMMAND'] == proc9['COMMAND_NAME']
    proc10 = ps[10]
    assert proc10['USER'] is None
    assert proc10['TTY'] is None
    assert proc10['%CPU'] is None
    assert proc10['%MEM'] is None
    assert proc10['COMMAND'] == proc10['COMMAND_NAME']


def test_psef_parser():
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps = Ps(None, None, None, ps_ef, None, None)
    len(ps.processes) == 6
    proc = ps[1]
    assert proc.get('UID') is None
    assert proc.get('C') is None
    assert proc.get('CMD') is None
    assert proc.get('STIME') is None
    assert proc['USER'] == 'root'
    assert proc['%CPU'] == 0
    assert proc['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'
    assert proc['START'] == '2019'


def test_psauxcww_and_ps_ef_parsers():
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps = Ps(None, None, None, ps_ef, ps_auxcww, None)
    assert len(ps.processes) == 7
    proc1 = ps[1]
    assert proc1['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'
    assert proc1['COMMAND_NAME'] == 'systemd'
    proc9 = ps[9]
    assert proc9['PPID'] == 2
    assert proc9['%CPU'] == 0.1
    assert proc9['%MEM'] == 0.0
    assert proc9['VSZ'] == 0.0
    proc12 = ps[12]
    assert proc12['PPID'] == 2
    assert proc12['%CPU'] == 0.0
    assert proc12['%MEM'] is None
    assert proc12['VSZ'] is None


def test_psalxwww_and_psauxww_and_psaux_parsers():
    ps_alxwww = PsAlxwww(context_wrap(PS_ALXWWW_LINES))
    ps_auxww = PsAuxww(context_wrap(PS_AUXWW_LINES))
    ps_aux = PsAux(context_wrap(PS_AUX_LINES))
    ps = Ps(ps_alxwww, ps_auxww, ps_aux, None, None, None)
    len(ps.processes) == 5
    ps = ps[1]
    assert ps['PID'] == 1
    assert ps['USER'] == 'root'
    assert ps['UID'] == 0
    assert ps['PPID'] == 0
    assert ps['%CPU'] == 0.1
    assert ps['%MEM'] == 0.0
    assert ps['VSZ'] == 195712.0
    assert ps['RSS'] == 7756.0
    assert ps['STAT'] == 'Ss'
    assert ps['TTY'] == '?'
    assert ps['START'] == '2019'
    assert ps['TIME'] == '478:05'
    assert ps['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'
    assert ps['COMMAND_NAME'] == 'systemd'
    assert ps['F'] == '4'
    assert ps['PRI'] == 20
    assert ps['NI'] == '0'
    assert ps['WCHAN'] == 'ep_pol'


def test_psauxwwwm_parser():
    ps_auxwwwm = PsAuxww(context_wrap(PS_AUXWWWM_LINES))
    ps = Ps(None, ps_auxwwwm, None, None, None, None)

    assert len(ps.processes) == 4

    ps_1 = ps[1]
    assert ps_1['PID'] == 1
    assert ps_1['USER'] == 'root'
    assert ps_1['%CPU'] == 1.8
    assert ps_1['%MEM'] == 0.8
    assert ps_1['VSZ'] == 24228.0
    assert ps_1['RSS'] == 15660.0
    assert ps_1['STAT'] == 'Ss'
    assert ps_1['TTY'] == '?'
    assert ps_1['START'] == '09:56'
    assert ps_1['TIME'] == '0:00'
    assert ps_1['COMMAND'] == '/usr/lib/systemd/systemd rhgb --switched-root --system --deserialize 31'
    assert ps_1['COMMAND_NAME'] == 'systemd'

    ps_4 = ps[4]
    assert ps_4['PID'] == 4
    assert ps_4['USER'] == 'root'
    assert ps_4['%CPU'] == 0.0
    assert ps_4['%MEM'] == 0.0
    assert ps_4['VSZ'] == 0.0
    assert ps_4['RSS'] == 0.0
    assert ps_4['STAT'] == 'I<'
    assert ps_4['TTY'] == '?'
    assert ps_4['START'] == '09:56'
    assert ps_4['TIME'] == '0:00'
    assert ps_4['COMMAND'] == '[rcu_par_gp]'
    assert ps_4['COMMAND_NAME'] == '[rcu_par_gp]'


def test_psalxwww_and_psauxww_and_psaux_and_psef_and_psauxcww_and_pseocmd_parsers():
    ps_alxwww = PsAlxwww(context_wrap(PS_ALXWWW_LINES))
    ps_auxww = PsAuxww(context_wrap(PS_AUXWW_LINES))
    ps_aux = PsAux(context_wrap(PS_AUX_LINES))
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps_eo_cmd = PsEoCmd(context_wrap(PS_EO_CMD_LINES, strip=False))
    ps = Ps(ps_alxwww, ps_auxww, ps_aux, ps_ef, ps_auxcww, ps_eo_cmd)
    len(ps.processes) == 8
    ps = ps[1]
    assert ps['PID'] == 1
    assert ps['USER'] == 'root'
    assert ps['UID'] == 0
    assert ps['PPID'] == 0
    assert ps['%CPU'] == 0.1
    assert ps['%MEM'] == 0.0
    assert ps['VSZ'] == 195712.0
    assert ps['RSS'] == 7756.0
    assert ps['STAT'] == 'Ss'
    assert ps['TTY'] == '?'
    assert ps['START'] == '2019'
    assert ps['TIME'] == '478:05'
    assert ps['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'
    assert ps['COMMAND_NAME'] == 'systemd'
    assert ps['F'] == '4'
    assert ps['PRI'] == 20
    assert ps['NI'] == '0'
    assert ps['WCHAN'] == 'ep_pol'
    assert ps['NLWP'] == '1'


def test_type_conversion():
    ps_alxwww = PsAlxwww(context_wrap(PS_ALXWWW_LINES))
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps = Ps(ps_alxwww, None, None, ps_ef, ps_auxcww, None)
    assert all(isinstance(p['PID'], int) for p in ps.processes)
    assert all(p['UID'] is None or isinstance(p['UID'], int) for p in ps.processes)
    assert all(p['PID'] is None or isinstance(p['PID'], int) for p in ps.processes)
    assert all(p['%CPU'] is None or isinstance(p['%CPU'], float) for p in ps.processes)
    assert all(p['%MEM'] is None or isinstance(p['%MEM'], float) for p in ps.processes)
    assert all(p['VSZ'] is None or isinstance(p['VSZ'], float) for p in ps.processes)
    assert all(p['RSS'] is None or isinstance(p['RSS'], float) for p in ps.processes)
    assert all(p['PRI'] is None or isinstance(p['PRI'], int) for p in ps.processes)


def test_combiner_api():
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps = Ps(None, None, None, None, ps_auxcww, None)
    assert ps.pids == [1, 2, 3, 8, 9, 11]
    assert len(ps.processes) == 6
    assert ps.processes[0]
    assert 'systemd' in ps.commands
    assert len(ps.search(USER='root')) == 6
    assert 'systemd' in ps
    assert ps[1] == {'%CPU': 0.1,
                     '%MEM': 0.0,
                     'ARGS': '',
                     'COMMAND': 'systemd',
                     'COMMAND_NAME': 'systemd',
                     'F': None,
                     'NI': None,
                     'PID': 1,
                     'PPID': None,
                     'PRI': None,
                     'RSS': 7756.0,
                     'START': '2019',
                     'STAT': 'Ss',
                     'TIME': '477:10',
                     'TTY': '?',
                     'UID': None,
                     'USER': 'root',
                     'VSZ': 195712.0,
                     'WCHAN': None,
                     'NLWP': None}
    assert ps[1000] is None
    assert [proc for proc in ps]


def test_docs():
    ps_alxwww = PsAlxwww(context_wrap(PS_ALXWWW_LINES))
    ps_auxww = PsAuxww(context_wrap(PS_AUXWW_LINES))
    ps_aux = PsAux(context_wrap(PS_AUX_LINES))
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps_eo_cmd = PsEoCmd(context_wrap(PS_EO_CMD_LINES, strip=False))
    ps_combiner = Ps(ps_alxwww, ps_auxww, ps_aux, ps_ef, ps_auxcww, ps_eo_cmd)
    env = {
        'ps_combiner': ps_combiner
    }
    failed, total = doctest.testmod(ps, globs=env)
    assert failed == 0


PS_ALXWWW_W_GREP = """
F   UID   PID  PPID PRI  NI    VSZ   RSS WCHAN  STAT TTY        TIME COMMAND
4     0     1     0  20   0 128292  6944 ep_pol Ss   ?          0:02 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
1     0     2     0  20   0      0     0 kthrea S    ?          0:00 [kthreadd]
1     0     3     2  20   0      0     0 smpboo S    ?          0:00 [ksoftirqd/0]
5     0     4     2  20   0      0     0 worker S    ?          0:00 [kworker/0:0]
1     0     5     2   0 -20      0     0 worker S<   ?          0:00 [kworker/0:0H]
4     0  1585     1  20   0  39336  3872 ep_pol Ss   ?          0:00 /usr/lib/systemd/systemd-journald
5     0  2964     1  16  -4  55520   900 ep_pol S<sl ?          0:00 /sbin/auditd
4     0  2966  2964  12  -8  84552   896 futex_ S<sl ?          0:00 /sbin/audispd
4     0  2968  2966  16  -4  55628  1404 unix_s S<   ?          0:00 /usr/sbin/sedispatch
4    81  3000     1  20   0  69800  3580 ep_pol Ssl  ?          0:00 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
4     0  3001     1  20   0  69800  3580 ep_pol Ssl  ?          0:00 grep -F COMMAND sedispatch audispd
"""


def test_search_ps_alxwww_w_grep():
    p = PsAlxwww(context_wrap(PS_ALXWWW_W_GREP))
    ps = Ps(p, None, None, None, None, None)
    assert len(ps.search(COMMAND_NAME__contains='dbus')) == 1


def test_psalxwww_and_psauxww_and_psaux_and_psef_and_psauxcww_and_ps_eo_cmd_parsers():
    ps_alxwww = PsAlxwww(context_wrap(PS_ALXWWW_LINES))
    ps_auxww = PsAuxww(context_wrap(PS_AUXWW_LINES))
    ps_aux = PsAux(context_wrap(PS_AUX_LINES))
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps_eo_cmd = PsEoCmd(context_wrap(PS_EO_CMD_LINES, strip=False))
    ps_combiner = Ps(ps_alxwww, ps_auxww, ps_aux, ps_ef, ps_auxcww, ps_eo_cmd)
    len(ps_combiner.processes) == 9
    ps = ps_combiner[1]
    assert ps['PID'] == 1
    assert ps['USER'] == 'root'
    assert ps['UID'] == 0
    assert ps['PPID'] == 0
    assert ps['%CPU'] == 0.1
    assert ps['%MEM'] == 0.0
    assert ps['VSZ'] == 195712.0
    assert ps['RSS'] == 7756.0
    assert ps['STAT'] == 'Ss'
    assert ps['TTY'] == '?'
    assert ps['START'] == '2019'
    assert ps['TIME'] == '478:05'
    assert ps['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'
    assert ps['COMMAND_NAME'] == 'systemd'
    assert ps['F'] == '4'
    assert ps['PRI'] == 20
    assert ps['NI'] == '0'
    assert ps['WCHAN'] == 'ep_pol'
    assert ps['NLWP'] == '1'

    assert ps_combiner[13]['COMMAND'] == '/usr/bin/python3.6'


def test_ps_all_parsers_combiner():
    ps_alxwww = PsAlxwww(context_wrap(PS_ALXWWW_LINES))
    ps_auxww = PsAuxww(context_wrap(PS_AUXWW_LINES))
    ps_aux = PsAux(context_wrap(PS_AUX_LINES))
    ps_ef = PsEf(context_wrap(PS_EF_LINES))
    ps_auxcww = PsAuxcww(context_wrap(PS_AUXCWW_LINES))
    ps_eo_cmd = PsEoCmd(context_wrap(PS_EO_CMD_LINES, strip=False))
    ps_combiner = Ps(ps_alxwww, ps_auxww, ps_aux, ps_ef, ps_auxcww, ps_eo_cmd)
    len(ps_combiner.processes) == 9
    ps = ps_combiner[1]
    assert ps['PID'] == 1
    assert ps['USER'] == 'root'
    assert ps['UID'] == 0
    assert ps['PPID'] == 0
    assert ps['%CPU'] == 0.1
    assert ps['%MEM'] == 0.0
    assert ps['VSZ'] == 195712.0
    assert ps['RSS'] == 7756.0
    assert ps['STAT'] == 'Ss'
    assert ps['TTY'] == '?'
    assert ps['START'] == '2019'
    assert ps['TIME'] == '478:05'
    assert ps['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'
    assert ps['COMMAND_NAME'] == 'systemd'
    assert ps['F'] == '4'
    assert ps['PRI'] == 20
    assert ps['NI'] == '0'
    assert ps['WCHAN'] == 'ep_pol'
    assert ps['NLWP'] == '1'

    assert ps_combiner[13]['COMMAND'] == '/usr/bin/python3.6'
