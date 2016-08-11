from falafel.mappers.dmesg import vmcore_dmesg
from falafel.tests import context_wrap

VMCORE_MSGINFO = """
[330011.041761] BUG: unable to handle kernel NULL pointer dereference at 0000000000000018
[330011.041808] RIP: [<ffffffff813143a8>] swiotlb_unmap_sg_attrs+0x28/0x60
[330011.041843] PGD 0
[330011.041857] Oops: 0000 [#1] SMP
[330011.041875] Modules linked in: iTCO_wdt iTCO_vendor_support intel_powerclamp coretemp kvm_intel ses enclosure kvm i2c_i801 sg pcspkr ioatdma lpc_ich mfd_core shpchp i7core_edac edac_core acpi_cpufreq ip_tables xfs libcrc32c sd_mod crc_t10dif crct10dif_generic crct10dif_common mgag200 syscopyarea sysfillrect sysimgblt drm_kms_helper crc32c_intel ttm serio_raw igb drm ptp pps_core cxgb3 3w_9xxx dca megaraid_sas i2c_algo_bit mdio i2c_core
[330011.042124] CPU: 4 PID: 0 Comm: swapper/4 Not tainted 3.10.0-327.13.1.el7.x86_64 #1
[330011.042153] Hardware name: Supermicro X8DT3/X8DT3, BIOS 2.0b    05/27/2011
[330011.042180] task: ffff8817bb6e3980 ti: ffff8817bb6f8000 task.ti: ffff8817bb6f8000
[330011.042207] RIP: 0010:[<ffffffff813143a8>]  [<ffffffff813143a8>] swiotlb_unmap_sg_attrs+0x28/0x60
[330011.042242] RSP: 0018:ffff88303fc03e00  EFLAGS: 00010002
[330011.042263] RAX: ffff8817bacfd098 RBX: 0000000000000000 RCX: 0000000000000001
[330011.042289] RDX: 0000000000000001 RSI: 0000000000000000 RDI: ffff8817bacfd098
[330011.042316] RBP: ffff88303fc03e28 R08: 0000000000000000 R09: ffffffff81314380
[330011.042342] R10: ffff882fb78d1c00 R11: 0000000000000000 R12: 0000000000000000
[330011.042368] R13: 0000000000000001 R14: 0000000000000001 R15: ffff8817bacfd098
[330011.042395] FS:  0000000000000000(0000) GS:ffff88303fc00000(0000) knlGS:0000000000000000
[330011.042424] CS:  0010 DS: 0000 ES: 0000 CR0: 000000008005003b
[330011.042446] CR2: 0000000000000018 CR3: 000000000194a000 CR4: 00000000000007e0
[330011.042473] DR0: 0000000000000000 DR1: 0000000000000000 DR2: 0000000000000000
[330011.042499] DR3: 0000000000000000 DR6: 00000000ffff0ff0 DR7: 0000000000000400
[330011.042526] Stack:
[330011.042536]  ffff882fb787c740 ffff882fb787c978 ffff882f66f49340 0000000000000047
[330011.042574]  0000000000000047 ffff88303fc03e38 ffffffff81421d96 ffff88303fc03ea8
[330011.042611]  ffffffffa006571f ffff88303fc03eb0 ffffffff8108e6dc ffff882fb787fdb0
ENERGY_PERF_BIAS: View and update with x86_energy_perf_policy(8)
[    0.025641] mce: CPU supports 22 MCE banks
[    0.025672] CPU0: Thermal monitoring enabled (TM1)
[    0.025697] Last level iTLB entries: 4KB 0, 2MB 0, 4MB 0
Last level dTLB entries: 4KB 64, 2MB 0, 4MB 0
tlb_flushall_shift: 6
""".strip()

vmcore_dmesg.filters.extend(["ENERGY_PERF_BIAS", "RIP", "CPU:"])


def test_vmcore_dmesg():
    vmcore_dmesg_info = vmcore_dmesg(context_wrap(VMCORE_MSGINFO))
    assert vmcore_dmesg_info.get("RIP") == [
        '[330011.041808] RIP: [<ffffffff813143a8>] swiotlb_unmap_sg_attrs+0x28/0x60',
        '[330011.042207] RIP: 0010:[<ffffffff813143a8>]  [<ffffffff813143a8>] swiotlb_unmap_sg_attrs+0x28/0x60']
    assert len(vmcore_dmesg_info.get("CPU:")) == 1
    assert vmcore_dmesg_info.has_startswith("ENERGY_PERF_BIAS")
    assert "0000000000000047" in vmcore_dmesg_info
