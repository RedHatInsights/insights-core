from insights.parsers.vmcore_dmesg import VMCoreDmesg
from insights.parsers import vmcore_dmesg
from insights.tests import context_wrap
import doctest


VMCORE_DMESG_TXT = """
[    0.000000]   A0000-BFFFF uncachable
[    0.000000]   C0000-DFFFF write-protect
[    0.000000]   E0000-FFFFF uncachable
[    0.000000] MTRR variable ranges enabled:
[    0.000000]   0 base 0000FE000000 mask 3FFFFF000000 uncachable
[    0.000000]   5 base 0000C0000000 mask 3FFFE0000000 uncachable
[    0.000000]   6 base 000080000000 mask 3FFFC0000000 uncachable
[    0.000000]   8 base 0000FF000000 mask 3FFFFF000000 uncachable
[    0.000000]   9 disabled
[    0.000000] PAT configuration [0-7]: WB  WC  UC- UC  WB  WP  UC- UC
[    0.000000] e820: last_pfn = 0x7b800 max_arch_pfn = 0x400000000
[    0.000000] Base memory trampoline at [ffff8d4380097000] 97000 size 24576
[    0.000000] Using GB pages for direct mapping
[    0.000000] BRK [0xabf22e000, 0xabf22efff] PGTABLE
[    0.000000] BRK [0xabf22f000, 0xabf22ffff] PGTABLE
[    0.000000] BRK [0xabf232000, 0xabf232fff] PGTABLE
""".strip()


VMCORE_DMESG_CRASH = """
[  345.691798] device-mapper: raid: Failed to read superblock of device at position 0
[  345.693497] device-mapper: raid: Discovered old metadata format; upgrading to extended metadata format
[  345.701166] md/raid1:mdX: active with 1 out of 2 mirrors
[  345.726870] BUG: unable to handle kernel NULL pointer dereference at 00000000000005ec
[  345.727782] IP: [<ffffffffc0852ffb>] read_balance+0x1db/0x4e0 [raid1]
[  345.728570] PGD 0
[  345.729279] Oops: 0000 [#1] SMP
[  345.729950] Modules linked in: raid1 dm_raid raid456 async_raid6_recov async_memcpy async_pq raid6_pq async_xor xor async_tx
[  345.734752]  drm_kms_helper syscopyarea sysfillrect sysimgblt fb_sys_fops ttm drm bfa ahci crct10dif_pclmul crct10dif_common
[  345.737334] CPU: 6 PID: 952 Comm: systemd-udevd Kdump: loaded Not tainted 3.10.0-862.9.1.el7.x86_64 #1
[  345.738198] Hardware name: Dell Inc. PowerEdge R730xd/072T6D, BIOS 2.4.3 01/17/2017
[  345.739334] task: ffff9f888d030fd0 ti: ffff9f86b76b4000 task.ti: ffff9f86b76b4000
""".strip()


TOKEN_KEYS = ['wp', 'conf', 'pg']
INDICATORS = ['write-protect', 'PAT configuration', 'BRK']


for key, indicator in zip(TOKEN_KEYS, INDICATORS):
    VMCoreDmesg.token_scan(key, indicator)


def test_vmcore_dmesg_lines():
    vm_core = VMCoreDmesg(context_wrap(VMCORE_DMESG_TXT))
    assert vm_core.lines == VMCORE_DMESG_TXT.splitlines()


def test_vmcore_dmesg_tokens():
    vm_core = VMCoreDmesg(context_wrap(VMCORE_DMESG_TXT))
    for key in TOKEN_KEYS:
        assert getattr(vm_core, key)


def test_vmcore_dmesg_doctest():
    env = {
        'vmcore_dmesg': VMCoreDmesg(context_wrap(VMCORE_DMESG_CRASH)),
    }
    failed, total = doctest.testmod(vmcore_dmesg, globs=env)
    assert failed == 0
