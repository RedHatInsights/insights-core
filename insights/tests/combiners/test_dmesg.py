from insights.tests import context_wrap
from insights.parsers.dmesg import DmesgLineList
from insights.parsers.dmesg_log import DmesgLog
from insights.combiners.dmesg import Dmesg

DMESG_LOG = """
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

DMESG_CMD = """
[    2.939498] [TTM] Initializing pool allocator
[    2.939502] [TTM] Initializing DMA pool allocator
[    2.940800] [drm] fb mappable at 0xFC000000
[    2.940947] fbcon: cirrusdrmfb (fb0) is primary device
[    2.957375] Console: switching to colour frame buffer device 128x48
[    2.959322] cirrus 0000:00:02.0: fb0: cirrusdrmfb frame buffer device
[    2.959334] [drm] Initialized cirrus 1.0.0 20110418 for 0000:00:02.0 on minor 0
[    3.062459] XFS (vda1): Ending clean mount
[    5.048484] ip6_tables: (C) 2000-2006 Netfilter Core Team
[    5.102434] Ebtables v2.0 registered
[    5.359444] IPv6: ADDRCONF(NETDEV_UP): eth0: link is not ready
[    5.406243] nf_conntrack version 0.5.0 (7933 buckets, 31732 max)
[    5.673082] Netfilter messages via NETLINK v0.30.
[    5.678631] ip_set: protocol 6
[   23.936112] random: crng init done
""".strip()


def test_dmesg_cmd():
    dmesg_cmd = DmesgLineList(context_wrap(DMESG_CMD))
    dmesg = Dmesg(dmesg_cmd, None)
    assert dmesg.dmesg_log_available is False
    assert hasattr(dmesg, "dmesg_log") is False
    assert dmesg.dmesg_cmd_available is True
    assert dmesg.dmesg_cmd_wrapped is True
    assert dmesg.dmesg_cmd is not False


def test_dmesg_log():
    dmesg_log = DmesgLog(context_wrap(DMESG_LOG))
    dmesg = Dmesg(None, dmesg_log)
    assert dmesg.dmesg_cmd_available is False
    assert hasattr(dmesg, "dmesg_cmd") is False
    assert dmesg.dmesg_log_available is True
    assert dmesg.dmesg_log_wrapped is False
    assert dmesg.dmesg_log is not False


def test_combined():
    dmesg_cmd = DmesgLineList(context_wrap(DMESG_CMD))
    dmesg_log = DmesgLog(context_wrap(DMESG_LOG))
    dmesg = Dmesg(dmesg_cmd, dmesg_log)
    assert dmesg.dmesg_cmd_available is True
    assert dmesg.dmesg_log_available is True


def test_empty():
    dmesg = Dmesg(None, None)
    assert dmesg.dmesg_cmd_available is False
    assert dmesg.dmesg_log_available is False
