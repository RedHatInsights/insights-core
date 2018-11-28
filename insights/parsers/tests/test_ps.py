from ...parsers import ps, ParseException
from ...tests import context_wrap
from ...util import keys_in
import pytest
import doctest

PsAuxww_TEST_DOC = """
 USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
 root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
 root      1661  0.0  0.0 126252  1392 ?        Ss   May31   0:04 /usr/sbin/crond -n
 root      1691  0.0  0.0  42688   172 ?        Ss   May31   0:00 /usr/sbin/rpc.mountd
 root      1821  0.0  0.0      0     0 ?        Z    May31   0:29 [kondemand/0]
 root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 /usr/sbin/irqbalance --foreground
 user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 /bin/bash
 root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 /usr/sbin/dhclient enp0s25
 root     20457  0.0  0.0   9120   832 ?        Ss   10:09   0:00 /bin/bash
"""

PsEf_TEST_DOC = """
UID         PID   PPID  C STIME TTY          TIME CMD
root          1      0  0 03:53 ?        00:00:06 /usr/lib/systemd/systemd --system --deserialize 15
root          2      0  0 03:53 ?        00:00:00 [kthreadd]
root       1803      1  5 03:54 ?        00:55:22 /usr/bin/openshift start master --config=/etc/origin/master/master-config.yaml --loglevel
root       1969      1  3 03:54 ?        00:33:51 /usr/bin/openshift start node --config=/etc/origin/node/node-config.yaml --loglevel=2
root       1995      1  0 03:54 ?        00:02:06 /usr/libexec/docker/rhel-push-plugin
root       2078   1969  0 03:54 ?        00:00:00 journalctl -k -f
root       7201      1  0 03:59 ?        00:00:00 /usr/bin/python /usr/libexec/rhsmd
root     111434      1  0 22:32 ?        00:00:00 nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf
nginx    111435 111434  0 22:32 ?        00:00:00 nginx: worker process
"""


def test_doc_examples():
    env = {
            'ps': ps.PsAuxww(context_wrap(PsAuxww_TEST_DOC)),
            'ps_auxww': ps.PsAuxww(context_wrap(PsAuxww_TEST_DOC)),
            'ps_ef': ps.PsEf(context_wrap(PsEf_TEST_DOC)),
          }
    failed, total = doctest.testmod(ps, globs=env)
    # XXX: these tests depend on the order of sets and dictionaries
    # I'm skipping them for now.
    # assert failed == 0


PsAuxww_TEST = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0 193892  5000 ?        Ss   Oct23   1:40 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
root         2  0.0  0.0      0     0 ?        S    Oct23   0:00 [kthreadd]
root       781  0.0  0.0 214308 10472 ?        Ss   Oct23   1:10 /usr/lib/systemd/systemd-journald
root      1111  0.0  0.0  24316  1400 ?        Ss   Oct23   0:00 /usr/sbin/smartd -n -q never
polkitd   1112  0.0  0.0 664820 14536 ?        Ssl  Oct23   2:35 /usr/lib/polkit-1/polkitd --no-debug
user_01   2713  2.4 19.2 12508144 3077224 ?    Sl   Nov21 533:33 /usr/lib64/firefox/firefox
root      8257  0.0  0.0 112876 14848 ?        S    08:18   0:00 /sbin/dhclient -d -q -sf /usr/libexec/nm-dhcp-helper -pf /var/run/dhclient-enp0s25.pid -lf /var/lib/NetworkManager/dhclient-bdb77870-4bb7-44e4-9f4f-d15ededcb42c-enp0s25.lease -cf /var/lib/NetworkManager/dhclient-enp0s25.conf enp0s25
"""


def test_ps_auxww_from_auxww():
    # test with input from `ps auxww`
    p = ps.PsAuxww(context_wrap(PsAuxww_TEST))
    d = p.data
    assert all('COMMAND' in row for row in d)
    assert keys_in([
        "USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY", "STAT", "START",
        "TIME", "COMMAND"
    ], d[0])
    assert d[0] == {
        '%MEM': '0.0', 'TTY': '?', 'VSZ': '193892', 'PID': '1', '%CPU': '0.0',
        'START': 'Oct23', 'USER': 'root', 'STAT': 'Ss', 'TIME': '1:40', 'RSS': '5000',
        'COMMAND': '/usr/lib/systemd/systemd --switched-root --system --deserialize 22',
        'COMMAND_NAME': 'systemd', 'ARGS': '--switched-root --system --deserialize 22',
    }
    assert d[2]["COMMAND"] == '/usr/lib/systemd/systemd-journald'
    assert d[-2] == {
        'USER': 'user_01', 'PID': '2713', '%CPU': '2.4', '%MEM': '19.2',
        'VSZ': '12508144', 'RSS': '3077224', 'TTY': '?', 'STAT': 'Sl',
        'START': 'Nov21', 'TIME': '533:33', 'COMMAND': '/usr/lib64/firefox/firefox',
        'COMMAND_NAME': 'firefox', 'ARGS': '',
    }
    assert p.fuzzy_match('kthreadd')
    assert '[kthreadd]' in p
    assert 'sshd' not in p
    assert not p.fuzzy_match("sshd")
    assert p.number_occurences("systemd") == 2
    assert p.number_occurences("openshift") != 2
    assert p.cpu_usage('/usr/lib64/firefox/firefox') == '2.4'
    assert p.cpu_usage('firefox') is None
    assert p.cpu_usage('dhclient') is None
    assert p.cpu_usage('java') is None
    assert p.running_pids() == ['1', '2', '781', '1111', '1112', '2713', '8257']

    # Test __iter__
    assert 13718356 == sum(int(proc['VSZ']) for proc in p)


PsEf_TEST = """
UID         PID   PPID  C STIME TTY          TIME CMD
root          1      0  0 03:53 ?        00:00:06 /usr/lib/systemd/systemd --system --deserialize 15
root          2      0  0 03:53 ?        00:00:00 [kthreadd]
root       1803      1  5 03:54 ?        00:55:22 /usr/bin/openshift start master --config=/etc/origin/master/master-config.yaml --loglevel
root       1969      1  3 03:54 ?        00:33:51 /usr/bin/openshift start node --config=/etc/origin/node/node-config.yaml --loglevel=2
root       1995      1  0 03:54 ?        00:02:06 /usr/libexec/docker/rhel-push-plugin
root       2078   1969  0 03:54 ?        00:00:00 journalctl -k -f
root       7201      1  0 03:59 ?        00:00:00 /usr/bin/python /usr/libexec/rhsmd
root     111434      1  0 22:32 ?        00:00:00 nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf
nginx    111435 111434  0 22:32 ?        00:00:00 nginx: worker process
"""


def test_ps_ef_from_ef():
    # test with input from `ps -ef`
    p = ps.PsEf(context_wrap(PsEf_TEST))
    d = p.data
    assert all('CMD' in row for row in d)
    assert keys_in([
        "UID", "PID", "PPID", "C", "STIME", "TTY", "TIME", "CMD"
    ], d[0])
    assert d[0] == {
        'UID': 'root', 'TTY': '?', 'PID': '1', 'PPID': '0',
        'TIME': '00:00:06', 'STIME': '03:53', 'C': '0',
        'CMD': '/usr/lib/systemd/systemd --system --deserialize 15',
        'COMMAND_NAME': 'systemd', 'ARGS': '--system --deserialize 15',
    }
    assert d[4]["CMD"] == '/usr/libexec/docker/rhel-push-plugin'
    assert d[-5] == {
        'TTY': '?', 'ARGS': '', 'UID': 'root',
        'CMD': '/usr/libexec/docker/rhel-push-plugin',
        'PID': '1995', 'C': '0', 'STIME': '03:54', 'TIME': '00:02:06',
        'PPID': '1', 'COMMAND_NAME': 'rhel-push-plugin'
    }
    assert p.fuzzy_match('kthreadd')
    assert p.number_occurences("systemd") != 2
    assert p.number_occurences("openshift") == 2
    assert p.parent_pid("111435") == ["111434", "nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf"]
    assert '[kthreadd]' in p
    assert 'sshd' not in p
    assert not p.fuzzy_match("sshd")
    assert p.running_pids() == ['1', '2', '1803', '1969', '1995', '2078', '7201', '111434', '111435']
    assert p.users("nginx: worker process") == {'nginx': ['111435']}


PsAuxcww_TEST = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 irqbalance
user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
user2    20161  0.0  0.0 108472  1896 pts/4    Ss   10:09   0:00 bash
user2    20164  0.0  0.0 108472  1896 pts/5    Ss   10:10   0:00 bash
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
qemu     22673  0.6 10.7 1618556 840452 ?      Sl   11:38   1:31 qemu-kvm
vdsm     27323 98.0 11.3  9120    987 ?        Ss   10.01   1:31 vdsm
""".strip()

PsAuxcww_BAD = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0
""".strip()

PsAuxcww_BAD_1 = """
root         1  0.0  0.0
""".strip()

PsAuxcww_BAD_2 = ""


def test_ps_auxww_from_auxcww():
    # test with input from `ps auxcww`
    p = ps.PsAuxww(context_wrap(PsAuxcww_TEST))
    d = p.data
    assert all('COMMAND' in row for row in d)
    assert keys_in([
        "USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY", "STAT", "START",
        "TIME", "COMMAND"
    ], d[0])
    assert d[0] == {
        '%MEM': '0.0', 'TTY': '?', 'VSZ': '19356', 'PID': '1', '%CPU': '0.0',
        'START': 'May31', 'COMMAND': 'init', 'COMMAND_NAME': 'init', 'USER': 'root', 'STAT': 'Ss',
        'TIME': '0:01', 'RSS': '1544', 'ARGS': '',
    }
    assert d[2]["COMMAND"] == 'irqbalance'
    assert d[-2]["COMMAND"] == 'qemu-kvm'
    assert p.fuzzy_match('irqbal')
    assert p.number_occurences("bash") == 3
    assert p.number_occurences("qemu-kvm") != 2
    assert 'dhclient' in p
    assert 'sshd' not in p
    assert not p.fuzzy_match("sshd")
    assert p.cpu_usage('dhclient') == '0.0'
    assert p.cpu_usage('java') is None

    assert p.users('bash') == {'user1': ['20160'], 'user2': ['20161', '20164']}


PS_AUXWWW = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  21452  1536 ?        Ss   Mar09   0:01 /sbin/init
root         2  0.0  0.0      0     0 ?        S    Mar09   0:00 [kthreadd]
root       501  0.0  0.0  11608  1684 ?        S<s  Mar09   0:00 /sbin/udevd -d
root      1319  0.0  0.0 326992  1684 ?        Sl   Mar09   0:00 /sbin/rsyslogd -i /var/run/syslogd.pid -c 5
dbus      1332  0.0  0.0  33740  1028 ?        Ssl  Mar09   0:00 dbus-daemon --system
root      1533  0.0  0.0   4060   584 tty4     Ss+  Mar09   0:00 /sbin/mingetty /dev/tty4
root      1606  0.0  0.0  83204  2432 ?        Ss   Mar09   0:00 login -- root
root      1610  0.0  0.0 108424  2104 tty1     Ss   Mar09   0:00 -bash
root      2573  1.6  1.0 342188 42020 tty1     S+   17:46   0:01 /usr/bin/python /usr/sbin/sosreport
"""


def test_ps_auxww_from_auxwww():
    # test with input from `ps auxwww`
    p = ps.PsAuxww(context_wrap(PS_AUXWWW))
    d = p.data
    assert all('COMMAND' in row for row in d)
    assert keys_in([
        "USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY", "STAT", "START",
        "TIME", "COMMAND"
    ], d[0])
    assert d[0] == {
        'USER': 'root', 'PID': '1', '%CPU': '0.0', '%MEM': '0.0',
        'VSZ': '21452', 'RSS': '1536', 'TTY': '?', 'STAT': 'Ss',
        'START': 'Mar09', 'TIME': '0:01', 'COMMAND': '/sbin/init',
        'COMMAND_NAME': 'init', 'ARGS': '',
    }
    assert p.fuzzy_match('kthread')
    assert '-bash' in p
    assert '/sbin/init' in p
    assert 'sshd' not in p
    assert 'kthread' not in p
    assert not p.fuzzy_match("sshd")
    assert p.number_occurences("python") == 1
    assert p.number_occurences("sshd") != 2
    assert p.fuzzy_match('python')

    assert p.search() == []
    assert p.search(COMMAND__contains='rsyslogd') == [p.data[3]]
    assert p.search(USER='root', COMMAND__contains='kthread') == [p.data[1]]
    assert p.search(TTY='tty1') == [p.data[7], p.data[8]]
    assert p.search(STAT__contains='Z') == []


PsAux_TEST = """
USER       PID %CPU %MEM     VSZ    RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0   19356   1544 ?        Ss   May31   0:01 /sbin/init
root      1821  0.0  0.0       0      0 ?        S    May31   0:25 [kondemand/0]
root      1864  0.0  0.0   18244    668 ?        Ss   May31   0:05 irqbalance --pid=/var/run/irqbalance.pid
user1    20160  0.0  0.0  108472   1896 pts/3    Ss   10:09   0:00 bash
root     20357  0.0  0.0    9120    760 ?        Ss   10:09   0:00 /sbin/dhclient -1 -q -lf /var/lib/dhclient/dhclient-extbr0.leases -pf /var/run/dhclient-extbr0.pid extbr0
qemu     22673  0.8 10.2 1618556 805636 ?        Sl   11:38   1:07 /usr/libexec/qemu-kvm -name rhel7 -S -M rhel6.5.0 -enable-kvm -m 1024 -smp 2,sockets=2,cores=1,threads=1 -uuid 13798ffc-bc1e-d437-4f3f-2e0fa6c923ad
tomcat    3662  1.0  5.7 2311488  58236 ?        Ssl  07:28   0:01 /usr/lib/jvm/jre/bin/java -classpath /usr/share/tomcat/bin/bootstrap.jar:/usr/share/tomcat/bin/tomcat-juli.jar:/usr/share/java/commons-daemon.jar -Dcatalina.base=/usr/share/tomcat -Dcatalina.home=/usr/share/tomcat -Djava.endorsed.dirs= -Djava.io.tmpdir=/var/cache/tomcat/temp -Djava.util.logging.config.file=/usr/share/tomcat/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager org.apache.catalina.startup.Bootstrap start
""".strip()


def test_ps_auxww_from_aux():
    # test with input from `ps aux`
    p = ps.PsAuxww(context_wrap(PsAux_TEST))
    d = p.data
    assert all('COMMAND' in row for row in d)
    assert keys_in([
        "USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY", "STAT", "START",
        "TIME", "COMMAND"
    ], d[0])
    assert d[0] == {
        '%MEM': '0.0', 'TTY': '?', 'VSZ': '19356', 'PID': '1', '%CPU': '0.0',
        'START': 'May31', 'COMMAND': '/sbin/init', 'COMMAND_NAME': 'init', 'USER': 'root',
        'STAT': 'Ss', 'TIME': '0:01', 'RSS': '1544', 'ARGS': ''
    }
    assert p.fuzzy_match('irqbal')
    assert 'bash' in p
    assert '/sbin/init' in p
    assert 'sshd' not in p
    assert 'kondemand' not in p
    assert not p.fuzzy_match("sshd")
    assert p.number_occurences("systemd") != 2
    assert p.number_occurences("bash") == 1
    assert p.fuzzy_match('kondemand')

    assert p.search() == []
    assert p.search(COMMAND__contains='java') == [p.data[6]]
    assert p.search(USER='root', COMMAND__contains='kondemand') == [p.data[1]]
    assert p.search(TTY='pts/3') == [p.data[3]]
    assert p.search(STAT__contains='Z') == []


PS_AUXWW_WITH_LATE_HEADER = '''
your 131072x1 screen size is bogus. expect trouble
USER        PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root          1  0.0  0.1 193704  5088 ?        Ss   Jan10   6:52 /usr/lib/systemd/systemd --switched-root --system --deserialize 21
root          2  0.0  0.0      0     0 ?        S    Jan10   0:02 [kthreadd]
root          3  0.0  0.0      0     0 ?        S    Jan10   0:29 [ksoftirqd/0]
root          5  0.0  0.0      0     0 ?        S<   Jan10   0:00 [kworker/0:0H]
root          7  0.0  0.0      0     0 ?        S    Jan10   0:00 [migration/0]
'''


def test_ps_auxww_with_late_header():
    p = ps.PsAuxww(context_wrap(PS_AUXWW_WITH_LATE_HEADER))
    assert '[kthreadd]' in p
    assert p.data[0]['COMMAND'] == '/usr/lib/systemd/systemd --switched-root --system --deserialize 21'


Ps_BAD = """
/bin/ps: command or file not found
"""


def test_ps_auxww_with_bad_input():
    # test with bad input
    d1 = ps.PsAuxww(context_wrap(PsAuxcww_BAD))
    assert 'test' not in d1

    with pytest.raises(ParseException) as exc:
        d2 = ps.PsAuxww(context_wrap(Ps_BAD))
        assert d2 is None
    assert 'PsAuxww: Cannot find ps header line in output' in str(exc)


PS_EO_NORMAL = """
  PID  PPID COMMAND
    1     0 systemd
    2     0 kthreadd
    3     2 ksoftirqd/0
    5     2 kworker/0:0H
    6     2 kworker/u2:0
 2416     1 auditd
 2419  2416 audispd
 2421  2419 sedispatch
 2892     1 NetworkManager
 3172  2892 dhclient
 3871     1 master
 3886  3871 qmgr
13724  3871 pickup
15663     2 kworker/0:1
16998     2 kworker/0:3
17259     2 kworker/0:0
18294  3357 sshd
18302 18294 sshd
18303 18302 bash
18338 18303 sudo
18346 18338 su
18347 18346 bash
18379 18347 ps
"""


def test_ps_eo():
    p = ps.PsEo(context_wrap(PS_EO_NORMAL))
    assert p is not None
    assert len(p.pid_info) == 23
    assert '15663' in p.pid_info
    assert p.pid_info['2416'] == {
        'PID': '2416', 'PPID': '1', 'COMMAND': 'auditd', 'COMMAND_NAME': 'auditd', 'ARGS': ''
    }
    assert p.pid_info['18379'] == {
        'PID': '18379', 'PPID': '18347', 'COMMAND': 'ps', 'COMMAND_NAME': 'ps', 'ARGS': ''
    }
    assert p.children('18347') == [
        {'PID': '18379', 'PPID': '18347', 'COMMAND': 'ps', 'COMMAND_NAME': 'ps', 'ARGS': ''}
    ]
    assert len(p.children('2')) == 6
