from insights.tests import context_wrap
from insights.parsers.dmesg_log import DmesgLog

DMESG_EXAMPLE = """
[    0.000000] Initializing cgroup subsys cpu
[    0.000000] Linux version 3.10.0-862.el7.x86_64 (mockbuild@x86-034.build.eng.bos.redhat.com) \
(gcc version 4.8.5 20150623 (Red Hat 4.8.5-28) (GCC) ) #1 SMP Wed Mar 21 18:14:51 EDT 2018
[    2.090905] SELinux:  Completing initialization.
[    2.090907] SELinux:  Setting up existing superblocks.
[    2.099684] systemd[1]: Successfully loaded SELinux policy in 82.788ms.
[    2.117410] ip_tables: (C) 2000-2006 Netfilter Core Team
[    2.117429] systemd[1]: Inserted module 'ip_tables'
[    2.376551] systemd-journald[441]: Received request to flush runtime journal from PID 1
[    2.716874] cryptd: max_cpu_qlen set to 100
[    2.804152] AES CTR mode by8 optimization enabled
[    2.874051] XFS (vda1): Mounting V5 Filesystem
[    2.919331] alg: No test for __gcm-aes-aesni (__driver-gcm-aes-aesni)
[    2.939496] [TTM] Zone  kernel: Available graphics memory: 507714 kiB
[    2.939498] [TTM] Initializing pool allocator
[    2.939502] [TTM] Initializing DMA pool allocator
""".strip()


def test_dmesg():
    dmesg_log = DmesgLog(context_wrap(DMESG_EXAMPLE))
    assert dmesg_log.get("SELinux")[1]["raw_message"] == "[    2.090907] SELinux:  Setting up existing superblocks."
    assert len(dmesg_log.get("TTM")) == 3
    assert "XFS" in dmesg_log
    assert "hpsa" not in dmesg_log
    assert dmesg_log.has_startswith("ip_tables")
    assert not dmesg_log.has_startswith("policy")
    assert dmesg_log.logs_startwith("cryptd") == ["cryptd: max_cpu_qlen set to 100"]
    assert dmesg_log.logs_startwith("perf") == []
    assert len(list(dmesg_log.get_after(2.919331))) == 4
    assert len(list(dmesg_log.get_after(2.919331, "TTM"))) == 3
