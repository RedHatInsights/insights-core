from __future__ import print_function
import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import lvm
from insights.tests import context_wrap
from insights.tests.parsers.lvm_test_data import LVMCONFIG, LVMCONFIG2, LVMCONFIG3

WARNINGS_CONTENT = """
WARNING
valid data 1
Checksum Error
valid data 2
  Failed to write
  Attempt To Close Device
valid data 3
""".strip()

WARNINGS_FOUND = """
WARNING
Checksum Error
  Failed to write
  Attempt To Close Device
""".strip()

VGSHEADING_CONTENT = """
Configuration setting "activation/thin_check_executable" unknown.
Configuration setting "activation/thin_check_options" unknown.
Configuration setting "activation/thin_check_executable" unknown.
Configuration setting "activation/thin_check_options" unknown.
WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  Using volume group(s) on command line.
Found duplicate PV qJMs5CEKY89qzq56E2vVeBvxzJGw2sA1: using /dev/mapper/mpathbp2 not /dev/cciss/c0d1p2
Using duplicate PV /dev/mapper/mpathbp2 from subsystem DM, ignoring /dev/cciss/c0d1p2
WARNING: Inconsistent metadata found for VG vgshared - updating to use version 26x
  Archiving volume group "vgshared" metadata (seqno 26).
  Archiving volume group "vgshared" metadata (seqno 27).
  Creating volume group backup "/etc/lvm/backup/vgshared" (seqno 27).
VG       Attr   Ext     #PV #LV #SN VSize   VFree   VG UUID                                VProfile #VMda VMdaFree  VMdaSize  #VMdaUse VG Tags
vg00     wz--n- 128.00m   1   7   0 279.00g   5.00g MiuKdK-ruw4-UG1i-0uLE-4dfB-bk2v-uxte2W              1   506.00k  1020.00k        1
vg00alt  wz--n-   4.00m   1   5   0 279.11g 265.11g LNzjbn-HU4C-WFCM-cRZ6-81ns-4rke-X8N0DA              1   507.00k  1020.00k        1
vg01     wz--n-   4.00m   2   1   0 199.99g 100.99g 7O9ePI-M1Kp-H9VH-Lxt3-pS1Z-nLQB-P1IIO3              2   508.00k  1020.00k        2
vgshared wz--nc   4.00m   6   1   0   1.76t 899.98g fFYYw3-Ns8Q-akPI-rrFU-YYn5-nKkk-UW67qO              6   507.00k  1020.00k        6
  Reloading config files
  Wiping internal VG cache
Configuration setting "activation/thin_check_executable" unknown.
Configuration setting "activation/thin_check_options" unknown.
""".strip()

VGSHEADING_CONTENT_DOC = """
WARNING: Locking disabled. Be careful! This could corrupt your metadata.
Using volume group(s) on command line.
VG            Attr   Ext   #PV #LV #SN VSize   VFree    VG UUID                                VProfile #VMda VMdaFree  VMdaSize  #VMdaUse VG Tags
DATA_OTM_VG   wz--n- 4.00m   6   1   0   2.05t 1020.00m xK6HXk-xl2O-cqW5-2izb-LI9M-4fV0-dAzfcc              6   507.00k  1020.00k        6
ITM_VG        wz--n- 4.00m   1   1   0  16.00g    4.00m nws5dd-INe6-1db6-9U1N-F0G3-S1z2-5XTdO4              1   508.00k  1020.00k        1
ORABIN_OTM_VG wz--n- 4.00m   2   3   0 190.00g       0  hfJwg8-hset-YgUY-X6NJ-gkWE-EunZ-KuCXGP              2   507.50k  1020.00k        2
REDO_OTM_VG   wz--n- 4.00m   1   3   0  50.00g       0  Q2YtGy-CWKU-sEYj-mqHk-rbdP-Hzup-wi8jsf              1   507.50k  1020.00k        1
SWAP_OTM_VG   wz--n- 4.00m   1   1   0  24.00g    8.00g hAerzZ-U8QU-ICkc-xxCj-N2Ny-rWzq-pmTpWJ              1   508.00k  1020.00k        1
rootvg        wz--n- 4.00m   1   6   0  19.51g    1.95g p4tLLb-ikeo-Ankk-2xJ6-iHYf-D4E6-KFCFvr              1   506.50k  1020.00k        1
Reloading config files
Wiping internal VG cache
""".strip()

LVS_HAEADING_OUTUPT = """
WARNING: Locking disabled. Be careful! This could corrupt your metadata.
LV          VG      Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert LV Tags Devices
lv_app      vg_root -wi-ao---- 71.63g                                                             /dev/sda2(7136)
lv_home     vg_root -wi-ao----  2.00g                                                             /dev/sda2(2272)
lv_opt      vg_root -wi-ao----  5.00g                                                             /dev/sda2(2784)
lv_root     vg_root -wi-ao----  5.00g                                                             /dev/sda2(0)
lv_tmp      vg_root -wi-ao----  1.00g                                                             /dev/sda2(4064)
lv_usr      vg_root -wi-ao----  5.00g                                                             /dev/sda2(4320)
lv_usrlocal vg_root -wi-ao----  1.00g                                                             /dev/sda2(5600)
lv_var      vg_root -wi-ao----  5.00g                                                             /dev/sda2(5856)
swap        vg_root -wi-ao----  3.88g                                                             /dev/sda2(1280)
""".strip()

CONTENT_WITH_EXTRA_LOCK_TIPS = """
WARNING: locking_type (0) is deprecated, using --nolocking.
WARNING: File locking is disabled.
Reading VG shared_vg1 without a lock.
LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='V1AMDw-e9x6-AdCq-p3Hr-6cYn-otra-ducLAc'|LVM2_VG_NAME='rhel'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_AUTOACTIVATION='enabled'|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SHARED=''|LVM2_VG_SIZE='<29.00g'|LVM2_VG_FREE='0 '|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCK_TYPE=''|LVM2_VG_LOCK_ARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='7423'|LVM2_VG_FREE_COUNT='0'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_VG_MISSING_PV_COUNT='0'|LVM2_LV_COUNT='2'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='3'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='507.50k'|LVM2_VG_MDA_SIZE='1020.00k'|LVM2_VG_MDA_COPIES='unmanaged'
"""

LVM_CONF = """
locking_type = 1
#locking_type = 2
# volume_list = [ "vg1", "vg2/lvol1", "@tag1", "@*" ]
volume_list = [ "vg2", "vg3/lvol3", "@tag2", "@*" ]
# filter = [ "a|loop|", "r|/dev/hdc|", "a|/dev/ide|", "r|.*|" ]

filter = [ "r/sda[0-9]*$/",  "a/sd.*/" ]
filter = [ "a/sda[0-9]*$/",  "r/sd.*/" ]
shell {
    history_size = 100
}
""".strip()

PVS_HEADINGS_OUTPUT = """
WARNING: Locking disabled. Be careful! This could corrupt your metadata.
Scanning all devices to update lvmetad.
No PV label found on /dev/loop0.
No PV label found on /dev/loop1.
No PV label found on /dev/sda1.
No PV label found on /dev/fedora/root.
No PV label found on /dev/sda2.
No PV label found on /dev/fedora/swap.
No PV label found on /dev/fedora/home.
No PV label found on /dev/mapper/docker-253:1-2361272-pool.
Wiping internal VG cache
Wiping cache of LVM-capable devices
PV                                                    VG     Fmt  Attr PSize   PFree DevSize PV UUID                                PMdaFree  PMdaSize  #PMda #PMdaUse PE
/dev/fedora/home                                                  ---       0     0  418.75g                                               0         0      0        0      0
/dev/fedora/root                                                  ---       0     0   50.00g                                               0         0      0        0      0
/dev/fedora/swap                                                  ---       0     0    7.69g                                               0         0      0        0      0
/dev/loop0                                                        ---       0     0  100.00g                                               0         0      0        0      0
/dev/loop1                                                        ---       0     0    2.00g                                               0         0      0        0      0
/dev/mapper/docker-253:1-2361272-pool                             ---       0     0  100.00g                                               0         0      0        0      0
/dev/mapper/luks-7430952e-7101-4716-9b46-786ce4684f8d fedora lvm2 a--  476.45g 4.00m 476.45g FPLCRf-d918-LVL7-6e3d-n3ED-aiZv-EesuzY        0   1020.00k     1        1 121970
/dev/sda1                                                         ---       0     0  500.00m                                               0         0      0        0      0
/dev/sda2                                                         ---       0     0  476.45g                                               0         0      0        0      0
Reloading config files
Wiping internal VG cache
""".strip()

VGS_OUTPUT = """
WARNING: Locking disabled. Be careful! This could corrupt your metadata.
Using volume group(s) on command line.
VG            Attr   Ext   #PV #LV #SN VSize   VFree    VG UUID                                VProfile #VMda VMdaFree  VMdaSize  #VMdaUse VG Tags
DATA_OTM_VG   wz--n- 4.00m   6   1   0   2.05t 1020.00m xK6HXk-xl2O-cqW5-2izb-LI9M-4fV0-dAzfcc              6   507.00k  1020.00k        6
ITM_VG        wz--n- 4.00m   1   1   0  16.00g    4.00m nws5dd-INe6-1db6-9U1N-F0G3-S1z2-5XTdO4              1   508.00k  1020.00k        1
ORABIN_OTM_VG wz--n- 4.00m   2   3   0 190.00g       0  hfJwg8-hset-YgUY-X6NJ-gkWE-EunZ-KuCXGP              2   507.50k  1020.00k        2
REDO_OTM_VG   wz--n- 4.00m   1   3   0  50.00g       0  Q2YtGy-CWKU-sEYj-mqHk-rbdP-Hzup-wi8jsf              1   507.50k  1020.00k        1
SWAP_OTM_VG   wz--n- 4.00m   1   1   0  24.00g    8.00g hAerzZ-U8QU-ICkc-xxCj-N2Ny-rWzq-pmTpWJ              1   508.00k  1020.00k        1
rootvg        wz--n- 4.00m   1   6   0  19.51g    1.95g p4tLLb-ikeo-Ankk-2xJ6-iHYf-D4E6-KFCFvr              1   506.50k  1020.00k        1
Reloading config files
Wiping internal VG cache
""".strip()

SYSTEM_DEVICES1 = """
# LVM uses devices listed in this file.
# Created by LVM command lvmdevices pid 2631 at Fri May 27 07:37:11 2022
VERSION=1.1.2
IDTYPE=devname IDNAME=/dev/vda2 DEVNAME=/dev/vda2 PVID=phl0clFbAokp9UXqbIgI5YYQxuTIJVkD PART=2
""".strip()

SYSTEM_DEVICES2 = """
# LVM uses devices listed in this file.
# Created by LVM command lvmdevices pid 2631 at Fri May 27 07:37:11 2022
VERSION=1.1.2
IDTYPE=sys_wwid IDNAME=/dev/vda2 DEVNAME=/dev/vda2 PVID=phl0clFbAokp9UXqbIgI5YYQxuTIJVkD PART=2
IDTYPE=sys_serial IDNAME=/dev/vda1 DEVNAME=/dev/vda1 PVID=phl0clFbAokp9UXqbIgI5YYQdeTIJVkD PART=1
""".strip()

SYSTEM_DEVICES3 = """
# LVM uses devices listed in this file.
# Created by LVM command lvmdevices pid 2631 at Fri May 27 07:37:11 2022
VERSION=1.1.2
""".strip()

LVM_FULLREPORT = """
{
    "report": [
        {
          "vg": [{"vg_fmt":"lvm2", "vg_uuid":"zclHZK-pMKd-fSIC-8TRX-xitj-RxY1-vwCRAw", "vg_name":"rhel", "vg_attr":"wz--n-"}],
          "pv": [{"pv_fmt":"lvm2", "pv_uuid":"LU7am7-ACyz-cPlb-byCA-j4IM-9FK8-iS1WA4", "dev_size":"<9.00g", "pv_name":"/dev/vda2"}],
          "lv": [{"lv_uuid":"kG4B7g-Ggar-uwtO-EbEX-gBX0-EGO2-Y0VFfU", "lv_name":"root", "lv_full_name":"rhel/root", "lv_path":"/dev/rhel/root"}],
          "pvseg": [{"pvseg_start":"0", "pvseg_size":"256", "pv_uuid":"LU7am7-ACyz-cPlb-byCA-j4IM-9FK8-iS1WA4", "lv_uuid":"8p6Tu0-OGa9-rbjg-5V22-D1dX-lNw7-Jed3m7"}],
          "seg": [{"segtype":"linear", "stripes":"1", "data_stripes":"1", "reshape_len":"", "reshape_len_le":"", "data_copies":"1"}]
        },
        {
          "vg": [{"vg_fmt":"lvm2", "vg_uuid":"1rLhOL-Mqkc-gi9I-Yspd-QZ3W-ZWN6-5viZiT", "vg_name":"vg1", "vg_attr":"wz--n-"}],
          "pv": [{"pv_fmt":"lvm2", "pv_uuid":"WwYITo-ng46-4Ufw-DqKx-0ZQA-LQeh-Vnga1N", "dev_size":"5.00g", "pv_name":"/dev/vdb"}],
          "lv": [{"lv_uuid":"tZdwGc-xGEg-VMQU-WIgE-k8kP-Udeo-hgLofA", "lv_name":"lvraid1", "lv_full_name":"vg1/lvraid1", "lv_path":"/dev/vg1/lvraid1"}],
          "pvseg": [{"pvseg_start":"0", "pvseg_size":"1", "pv_uuid":"D39Poc-PupR-sYD5-bUeJ-2aYO-YWdP-XAInA5", "lv_uuid":"3YHTyV-HXoc-wRRH-D1Jw-NNIs-m2g8-cOvgGS"}],
          "seg": [{"segtype":"linear", "stripes":"1", "data_stripes":"1", "reshape_len":"", "reshape_len_le":"", "data_copies":"1"}]
        }
    ]
}
""".strip()

LVM_FULLREPORT_WARNING = """
WARNING: locking_type(0) is deprecated, using - -nolocking.
{
    "report": [
        {
          "vg": [{"vg_fmt":"lvm2", "vg_uuid":"zclHZK-pMKd-fSIC-8TRX-xitj-RxY1-vwCRAw", "vg_name":"rhel", "vg_attr":"wz--n-"}],
          "pv": [{"pv_fmt":"lvm2", "pv_uuid":"LU7am7-ACyz-cPlb-byCA-j4IM-9FK8-iS1WA4", "dev_size":"<9.00g", "pv_name":"/dev/vda2"}],
          "lv": [{"lv_uuid":"kG4B7g-Ggar-uwtO-EbEX-gBX0-EGO2-Y0VFfU", "lv_name":"root", "lv_full_name":"rhel/root", "lv_path":"/dev/rhel/root"}],
          "pvseg": [{"pvseg_start":"0", "pvseg_size":"256", "pv_uuid":"LU7am7-ACyz-cPlb-byCA-j4IM-9FK8-iS1WA4", "lv_uuid":"8p6Tu0-OGa9-rbjg-5V22-D1dX-lNw7-Jed3m7"}],
          "seg": [{"segtype":"linear", "stripes":"1", "data_stripes":"1", "reshape_len":"", "reshape_len_le":"", "data_copies":"1"}]
        },
        {
          "vg": [{"vg_fmt":"lvm2", "vg_uuid":"1rLhOL-Mqkc-gi9I-Yspd-QZ3W-ZWN6-5viZiT", "vg_name":"vg1", "vg_attr":"wz--n-"}],
          "pv": [{"pv_fmt":"lvm2", "pv_uuid":"WwYITo-ng46-4Ufw-DqKx-0ZQA-LQeh-Vnga1N", "dev_size":"5.00g", "pv_name":"/dev/vdb"}],
          "lv": [{"lv_uuid":"tZdwGc-xGEg-VMQU-WIgE-k8kP-Udeo-hgLofA", "lv_name":"lvraid1", "lv_full_name":"vg1/lvraid1", "lv_path":"/dev/vg1/lvraid1"}],
          "pvseg": [{"pvseg_start":"0", "pvseg_size":"1", "pv_uuid":"D39Poc-PupR-sYD5-bUeJ-2aYO-YWdP-XAInA5", "lv_uuid":"3YHTyV-HXoc-wRRH-D1Jw-NNIs-m2g8-cOvgGS"}],
          "seg": [{"segtype":"linear", "stripes":"1", "data_stripes":"1", "reshape_len":"", "reshape_len_le":"", "data_copies":"1"}]
        }
    ]
}
""".strip()

LVM_FULLREPORT_EMPTY = """
{
    "report": [
    ]
}
""".strip()


def test_find_warnings():
    data = [l for l in lvm.find_warnings(WARNINGS_CONTENT.splitlines())]
    assert len(data) == len(WARNINGS_FOUND.splitlines())
    assert data == WARNINGS_FOUND.splitlines()


def compare_partial_dicts(result, expected):
    """
    Make sure all the keys in expected are matched by keys in result, and
    that the values stored in those keys match.  Result can contain more
    items than expected - those are ignored.

    Used in the test_lvs, test_pvs and test_vgs tests.
    """
    # return all(result[k] == expected[k] for k in expected.keys())
    mismatches = 0
    for k in expected.keys():
        if not result[k] == expected[k]:
            print("Failed for key {k}, {r} != {e}".format(k=k, r=result[k], e=expected[k]))
            mismatches += 1
    return mismatches == 0


def test_lvmconfig():
    p = lvm.LvmConfig(context_wrap(LVMCONFIG))
    assert p.data["dmeventd"]["raid_library"] == "libdevmapper-event-lvm2raid.so"
    assert p.data["global"]["thin_check_options"] == ["-q", "--clear-needs-check-flag"]


def test_lvmconfig_2():
    p = lvm.LvmConfig(context_wrap(LVMCONFIG2))
    assert p.data['global']['umask'] == '077'


def test_lvmconfig_exception():
    with pytest.raises(ParseException):
        lvm.LvmConfig(context_wrap(LVMCONFIG3))


def test_vgsheading_warnings():
    result = lvm.VgsHeadings(context_wrap(VGSHEADING_CONTENT))
    assert len(result.warnings) == 6
    assert 'Configuration setting "activation/thin_check_executable" unknown.' in result.warnings
    assert 'WARNING: Locking disabled. Be careful! This could corrupt your metadata.' in result.warnings


def test_vgs_with_extra_tips():
    result = lvm.Vgs(context_wrap(CONTENT_WITH_EXTRA_LOCK_TIPS))
    assert result is not None
    assert len(result.data.get('warnings')) == 3
    assert 'Reading VG shared_vg1 without a lock.' in result.data.get('warnings')
    assert len(result.data.get('content')) == 1


def test_system_devices():
    devices = lvm.LvmSystemDevices(context_wrap(SYSTEM_DEVICES2))
    assert len(devices) == 2
    assert '/dev/vda1' in devices
    assert devices['/dev/vda1']['IDTYPE'] == 'sys_serial'
    assert '/dev/vda2' in devices
    assert devices['/dev/vda2']['IDTYPE'] == 'sys_wwid'


def test_system_devices_exception():
    with pytest.raises(SkipComponent):
        lvm.LvmSystemDevices(context_wrap(SYSTEM_DEVICES3))


def test_lvm_fullreport():
    for data in [LVM_FULLREPORT, LVM_FULLREPORT_WARNING]:
        report = lvm.LvmFullReport(context_wrap(data))
        assert report is not None
        assert len(report.volume_groups) == 2
        assert 'vg1' in report.volume_groups and 'rhel' in report.volume_groups
        vg1 = report.volume_groups['vg1']
        assert set(vg1.keys()) == set(['vg', 'pv', 'lv', 'pvseg', 'seg'])
        assert vg1['vg'][0]['vg_name'] == 'vg1'
        assert vg1['pv'][0]['pv_name'] == '/dev/vdb'
        assert vg1['lv'][0]['lv_name'] == 'lvraid1'
        assert vg1['pvseg'][0] == {
            "pvseg_start": "0",
            "pvseg_size": "1",
            "pv_uuid": "D39Poc-PupR-sYD5-bUeJ-2aYO-YWdP-XAInA5",
            "lv_uuid": "3YHTyV-HXoc-wRRH-D1Jw-NNIs-m2g8-cOvgGS"
        }
        assert vg1['seg'][0]['data_stripes'] == '1'

        if data == LVM_FULLREPORT_WARNING:
            assert report.warnings == [LVM_FULLREPORT_WARNING.splitlines()[0], ]


def test_lvm_fullreport_empty():
    with pytest.raises(SkipComponent):
        lvm.LvmFullReport(context_wrap(LVM_FULLREPORT_EMPTY))


def test_docs():
    env = {
        'devices': lvm.LvmSystemDevices(context_wrap(SYSTEM_DEVICES1)),
        'lvm_conf_data': lvm.LvmConf(context_wrap(LVM_CONF)),
        'pvs_data': lvm.PvsHeadings(context_wrap(PVS_HEADINGS_OUTPUT)),
        'vgs_info': lvm.VgsHeadings(context_wrap(VGSHEADING_CONTENT_DOC)),
        'lvs_info': lvm.LvsHeadings(context_wrap(LVS_HAEADING_OUTUPT)),
        'lvm_fullreport': lvm.LvmFullReport(context_wrap(LVM_FULLREPORT)),
    }
    failed, total = doctest.testmod(lvm, globs=env)
    assert failed == 0
