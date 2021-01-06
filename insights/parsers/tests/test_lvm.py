from __future__ import print_function
from insights.parsers import lvm
from insights.tests import context_wrap
from .lvm_test_data import LVMCONFIG

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


def test_vgsheading_warnings():
    result = lvm.VgsHeadings(context_wrap(VGSHEADING_CONTENT))
    assert len(result.warnings) == 6
    assert 'Configuration setting "activation/thin_check_executable" unknown.' in result.warnings
    assert 'WARNING: Locking disabled. Be careful! This could corrupt your metadata.' in result.warnings
