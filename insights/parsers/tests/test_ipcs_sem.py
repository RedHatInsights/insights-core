from insights.parsers.ipcs_sem import IpcsS, IpcsSI
from insights.tests import context_wrap

IPCS_S = """
------ Semaphore Arrays --------
key        semid      owner      perms      nsems
0x00000000 557056     apache     600        1
0x00000000 589825     apache     600        1
0x00000000 131074     apache     600        1
0x0052e2c1 163843     postgres   600        17
0x0052e2c2 196612     postgres   600        17
0x0052e2c3 229381     postgres   600        17
0x0052e2c4 262150     postgres   600        17
0x0052e2c5 294919     postgres   600        17
0x0052e2c6 327688     postgres   600        17
0x0052e2c7 360457     postgres   600        17
0x00000000 622602     apache     600        1
0x00000000 655371     apache     600        1
0x00000000 688140     apache     600        1
""".strip()

IPCS_S_I = """
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
""".strip()


def test_ipcs_s():
    sem = IpcsS(context_wrap(IPCS_S))

    assert '131074' in sem
    assert '11074' not in sem
    assert sem.get('262150') == {'owner': 'postgres', 'perms': '600',
                                 'nsems': '17', 'key': '0x0052e2c4'}
    assert sem['622602'] == {'owner': 'apache', 'perms': '600',
                             'nsems': '1', 'key': '0x00000000'}


def test_ipcs_si():
    sem = IpcsSI(context_wrap(IPCS_S_I))

    assert sem.semid == '65536'
    assert sem.pid_list == ['0', '2265', '4390', '6151', '6152']
