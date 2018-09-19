from insights.parsers.ipcs import IpcsSI, IpcsS
from insights.parsers.ps import PsAuxcww
from insights.combiners import ipcs_semaphores
from insights.combiners.ipcs_semaphores import IpcsSemaphores
from insights.tests import context_wrap
import doctest

PsAuxcww_OUT = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      6152  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root      2265  0.0  0.0  18244   668 ?        Ss   May31   0:05 irqbalance
""".strip()

IPCS_S = """
------ Semaphore Arrays --------
key        semid      owner      perms      nsems
0x00000000 557056     apache     600        4
0x00000000 655371     apache     600        1
0x0052e2c1 65536      postgres   600        8
0x00000000 622502     apache     600        1
0x00000000 622602     apache     600        1
0x00000000 688140     apache     600        1
""".strip()

IPCS_S_I_1 = """
Semaphore Array semid=557056
uid=500  gid=501     cuid=500    cgid=501
mode=0600, access_perms=0600
nsems = 4
otime = Sun May 12 14:44:53 2013
ctime = Wed May  8 22:12:15 2013
semnum     value      ncount     zcount     pid
0          1          0          0          0
1          1          0          0          0
4          1          0          0          0
5          1          0          0          0
"""

IPCS_S_I_2 = """
Semaphore Array semid=65536
uid=500  gid=501     cuid=500    cgid=501
mode=0600, access_perms=0600
nsems = 8
otime = Sun May 12 14:44:53 2013
ctime = Wed May  8 22:12:15 2013
semnum     value      ncount     zcount     pid
0          1          0          0          0
1          1          0          0          0
0          1          0          0          6151
3          1          0          0          2265
4          1          0          0          0
5          1          0          0          0
0          0          7          0          6152
7          1          0          0          4390

"""

IPCS_S_I_3 = """
Semaphore Array semid=622502
uid=48   gid=48  cuid=0  cgid=0
mode=0600, access_perms=0600
nsems = 1
otime = Wed Apr 12 15:41:03 2017
ctime = Wed Apr 12 15:41:03 2017
semnum     value      ncount     zcount     pid
0          1          0          0          6151

"""

IPCS_S_I_4 = """
Semaphore Array semid=622602
uid=48   gid=48  cuid=0  cgid=0
mode=0600, access_perms=0600
nsems = 1
otime = Wed Apr 12 15:41:03 2017
ctime = Wed Apr 12 15:41:03 2017
semnum     value      ncount     zcount     pid
0          1          0          0          6151

"""

IPCS_S_I_5 = """
Semaphore Array semid=655371
uid=48   gid=48  cuid=0  cgid=0
mode=0600, access_perms=0600
nsems = 1
otime = Not set
ctime = Wed Apr 12 15:41:03 2017
semnum     value      ncount     zcount     pid
0          1          0          0          991

"""

IPCS_S_I_6 = """
Semaphore Array semid=688140
uid=48   gid=48  cuid=0  cgid=0
mode=0600, access_perms=0600
nsems = 1
otime = Wed Apr 12 16:01:28 2017
ctime = Wed Apr 12 15:41:03 2017
semnum     value      ncount     zcount     pid
0          0          7          0          6152
""".strip()


def test_ipcs_semaphores():
    sem1 = IpcsSI(context_wrap(IPCS_S_I_1))
    sem2 = IpcsSI(context_wrap(IPCS_S_I_2))
    sem3 = IpcsSI(context_wrap(IPCS_S_I_3))
    sem4 = IpcsSI(context_wrap(IPCS_S_I_4))
    sem5 = IpcsSI(context_wrap(IPCS_S_I_5))
    sem6 = IpcsSI(context_wrap(IPCS_S_I_6))
    sems = IpcsS(context_wrap(IPCS_S))
    ps = PsAuxcww(context_wrap(PsAuxcww_OUT))
    rst = IpcsSemaphores(sems, [sem1, sem2, sem3, sem4, sem5, sem6], ps)
    assert rst.get_sem('65536').pid_list == ['0', '2265', '4390', '6151', '6152']
    assert rst.count_of_all_sems() == 6
    assert rst.count_of_all_sems(owner='apache') == 5
    assert rst.count_of_orphan_sems() == 3
    assert rst.count_of_orphan_sems('postgres') == 0
    i = 0
    for sem in rst:
        i += 1
    assert i == rst.count_of_all_sems()
    assert rst.orphan_sems() == ['622502', '622602', '655371']
    assert rst.orphan_sems('apache') == ['622502', '622602', '655371']
    assert rst.orphan_sems('postgres') == []


def test_doc_examples():
    sem1 = IpcsSI(context_wrap(IPCS_S_I_1))
    sem2 = IpcsSI(context_wrap(IPCS_S_I_2))
    sem3 = IpcsSI(context_wrap(IPCS_S_I_3))
    sem4 = IpcsSI(context_wrap(IPCS_S_I_4))
    sem6 = IpcsSI(context_wrap(IPCS_S_I_6))
    sems = IpcsS(context_wrap(IPCS_S))
    ps = PsAuxcww(context_wrap(PsAuxcww_OUT))
    env = {
            'oph_sem': IpcsSemaphores(sems,
                        [sem1, sem2, sem3, sem4, sem6], ps)
          }
    failed, total = doctest.testmod(ipcs_semaphores, globs=env)
    assert failed == 0
