from ...mappers import ps
from ...tests import context_wrap
from ...util import keys_in

import unittest

SERVICE_RUNNING = 'SERVICE_RUNNING'
SERVICES_RUNNING = 'SERVICES_RUNNING'

PsAuxcww_BAD = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0
""".strip()

PsAuxcww_TEST = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 irqbalance
user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
user2    20161  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
qemu     22673  0.6 10.7 1618556 840452 ?      Sl   11:38   1:31 qemu-kvm
vdsm     27323 98.0 11.3  9120    987 ?        Ss   10.01   1:31 vdsm
""".strip()

PsAux_TEST = """
USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 /sbin/init
root      1821  0.0  0.0      0     0 ?        S    May31   0:25 [kondemand/0]
root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 irqbalance --pid=/var/run/irqbalance.pid
user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
root     20357  0.0  0.0   9120   760 ?        Ss   10:09   0:00 /sbin/dhclient -1 -q -lf /var/lib/dhclient/dhclient-extbr0.leases -pf /var/run/dhclient-extbr0.pid extbr0
qemu     22673  0.8 10.2 1618556 805636 ?      Sl   11:38   1:07 /usr/libexec/qemu-kvm -name rhel7 -S -M rhel6.5.0 -enable-kvm -m 1024 -smp 2,sockets=2,cores=1,threads=1 -uuid 13798ffc-bc1e-d437-4f3f-2e0fa6c923ad
""".strip()

PsAxcwwo_TEST = """
COMMAND         %CPU                  STARTED
systemd          0.0 Thu Dec  8 01:19:25 2016
kthreadd         0.0 Thu Dec  8 01:19:25 2016
ksoftirqd/0      0.0 Thu Dec  8 01:19:25 2016
libvirtd         0.0 Wed Dec 28 05:59:04 2016
vdsm             1.3 Wed Dec 28 05:59:06 2016
""".strip()

Ps_BAD = """
/bin/ps: command or file not found
"""


class TestPS(unittest.TestCase):
    def test_ps_auxcww(self):
        p = ps.PsAuxcww(context_wrap(PsAuxcww_TEST))
        d = p.data
        self.assertTrue(keys_in(["USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY", "STAT", "START", "TIME", "COMMAND"], d[0]))
        self.assertEqual(d[0], {'%MEM': '0.0', 'TTY': '?', 'VSZ': '19356', 'PID': '1', '%CPU': '0.0', 'START': 'May31', 'COMMAND': 'init', 'USER': 'root', 'STAT': 'Ss', 'TIME': '0:01', 'RSS': '1544'})
        self.assertEqual(d[2]["COMMAND"], 'irqbalance')
        self.assertEqual(d[-2]["COMMAND"], 'qemu-kvm')
        self.assertTrue(p.fuzzy_match('irqbal'))
        self.assertIn('dhclient', p)
        self.assertEqual(sorted([c['COMMAND'] for c in p]), sorted([
            'init', 'kondemand/0', 'irqbalance', 'bash', 'bash', 'dhclient',
            'qemu-kvm', 'vdsm'
        ]))
        self.assertNotIn('sshd', p)
        self.assertFalse(p.fuzzy_match("sshd"))

        d1 = ps.PsAuxcww(context_wrap(PsAuxcww_BAD))
        self.assertNotIn('test', d1)

    def test_ps_aux(self):
        d = ps.PsAux(context_wrap(PsAux_TEST)).data
        self.assertTrue(keys_in(["USER", "PID", "%CPU", "%MEM", "VSZ", "RSS", "TTY", "STAT", "START", "TIME", "COMMAND"], d[0]))
        self.assertEqual(d[0], {'%MEM': '0.0', 'TTY': '?', 'VSZ': '19356', 'PID': '1', '%CPU': '0.0', 'START': 'May31', 'COMMAND': '/sbin/init', 'USER': 'root', 'STAT': 'Ss', 'TIME': '0:01', 'RSS': '1544'})
        self.assertEqual(d[2]["COMMAND"], 'irqbalance --pid=/var/run/irqbalance.pid')
        self.assertEqual(d[-1]["COMMAND"].split()[0], "/usr/libexec/qemu-kvm")
        self.assertEqual(d[-1]["COMMAND"].split()[-2:], ["-uuid", "13798ffc-bc1e-d437-4f3f-2e0fa6c923ad"])
        d1 = ps.PsAux(context_wrap(""))
        self.assertEqual(d1.data, [])

    def test_running_procs(self):
        proc_list = ps.PsAuxcww(context_wrap(PsAuxcww_TEST)).running
        for proc in ["init", "kondemand/0", "irqbalance", "bash", "dhclient", "qemu-kvm"]:
            self.assertTrue(proc in proc_list)
        for proc in ["dummy-proc", "kondemand"]:
            self.assertFalse(proc in proc_list)

    def test_cpu_usage(self):
        self.assertEqual(ps.PsAuxcww(context_wrap(PsAuxcww_TEST)).cpu_usage("vdsm"), "98.0")

    def test_ps_axcwwo(self):
        d = ps.PsAxcwwo(context_wrap(PsAxcwwo_TEST)).data
        self.assertTrue(keys_in(["COMMAND", "%CPU", "STARTED"], d[0]))
        self.assertEqual(d[0], {'STARTED': 'Thu Dec  8 01:19:25 2016', 'COMMAND': 'systemd', '%CPU': '0.0'})
        self.assertEqual(d[2]["COMMAND"], 'ksoftirqd/0')
        self.assertEqual(d[-2]["COMMAND"], 'libvirtd')
        with self.assertRaises(ValueError):
            d1 = ps.PsAxcwwo(context_wrap("test"))
            self.assertEqual(d1.data, [])

    def test_ps_aux_bad(self):
        p = ps.PsAux(context_wrap(Ps_BAD))
        self.assertIsNotNone(p)
        self.assertEqual(p.data, [])

    def test_ps_auxcwwo_bad(self):
        with self.assertRaisesRegexp(ValueError, 'PsAuxcww: Unable to parse 1 line'):
            p = ps.PsAxcwwo(context_wrap(Ps_BAD))
            self.assertIsNone(p)

    def test_ps_auxcww_exception(self):
        with self.assertRaises(ValueError):
            self.assertIsNone(
                ps.PsAuxcww(context_wrap('Unknown HZ value! (771) Assume 100'))
            )

    def test_users(self):
        ps_obj = ps.PsAuxcww(context_wrap(PsAuxcww_TEST))
        self.assertEqual(ps_obj.users("qemu-kvm"), {'qemu': ['22673']})
        self.assertEqual(ps_obj.users("sshd"), {})

    def test_ps_auxcww_pid(self):
        ps_auxcww = ps.PsAuxcww(context_wrap(PsAuxcww_TEST))
        self.assertEqual(ps_auxcww.running_pids(), ['1', '1821', '1864', '20160', '20161', '20357', '22673', '27323'])

    def test_ps_auxcww_alternate(self):
        ps_auxcww = ps.PsAuxcww(context_wrap(PsAuxcww_TEST))
        self.assertEqual(ps_auxcww.services, [
            ('init', 'root', 'root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init'),
            ('kondemand/0', 'root', 'root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0'),
            ('irqbalance', 'root', 'root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 irqbalance'),
            ('bash', 'user1', 'user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash'),
            ('bash', 'user2', 'user2    20161  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash'),
            ('dhclient', 'root', 'root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient'),
            ('qemu-kvm', 'qemu', 'qemu     22673  0.6 10.7 1618556 840452 ?      Sl   11:38   1:31 qemu-kvm'),
            ('vdsm', 'vdsm', 'vdsm     27323 98.0 11.3  9120    987 ?        Ss   10.01   1:31 vdsm')
        ])
