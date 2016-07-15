from falafel.util import parse_table
from falafel.core.plugins import mapper


@mapper('pvs')
def pvs(context):
    """
    - Parse each line in the output of pvs

    ---------------- Output sample of pvs ---------------

    PV         VG                Fmt  Attr PSize   PFree
    /dev/sda2  rhel_hp-dl160g8-3 lvm2 a--  465.27g 44.00m
    /dev/sda3  rhel_hp-dl180g8-4 lvm2 a--  200.18g 40.00m

    -----------------------------------------------------

    - Returns a list like:
    [
        {
            'PV'    : '/dev/sda2',
            'VG'    : 'rhel_hp-dl160g8-3',
            'Fmt'   : 'lvm2',
            'Attr'  : 'a--',
            'PSize' : '465.27g',
            'PFree' : '44.00m'
        },
        {
            'PV'    : '/dev/sda3',
            'VG'    : 'rhel_hp-dl160g8-4',
            'Fmt'   : 'lvm2',
            'Attr'  : 'a--',
            'PSize' : '200.18g',
            'PFree' : '40.00m'
        }
    ]

    """
    return parse_table(context.content)


@mapper('lvs')
def lvs(context):
    """
    The CommandSpec of "lvs" defined as:
    lvs -a -o lv_name,vg_name,lv_size,region_size,mirror_log,lv_attr,devices

    Parse each line in the output of lvs based on the CommandSpec of "lvs" in
    specs.py:

    ---------------------------------- Output sample of lvs -----------------------------------
    LV             VG       LSize   Region  Log      Attr       Devices
    lv0            vg0       52.00m 512.00k lv0_mlog mwi-a-m--- lv0_mimage_0(0),lv0_mimage_1(0)
    [lv0_mimage_0] vg0       52.00m      0           iwi-aom--- /dev/sdb1(0)
    [lv0_mimage_1] vg0       52.00m      0           iwi-aom--- /dev/sdb2(0)
    [lv0_mlog]     vg0        4.00m      0           lwi-aom--- /dev/sdb3(3)

    lv1            vg0       20.00m   2.00m lv1_mlog mwi-a-m--- lv1_mimage_0(0),lv1_mimage_1(0)
    [lv1_mimage_0] vg0       20.00m      0           iwi-aom--- /dev/sdb1(13)
    [lv1_mimage_1] vg0       20.00m      0           iwi-aom--- /dev/sdb2(13)
    [lv1_mlog]     vg0        4.00m      0           lwi-aom--- /dev/sdb3(0)
    lv_root        vg_test1   6.71g      0           -wi-ao---- /dev/sda2(0)
    lv_swap        vg_test1 816.00m      0           -wi-ao---- /dev/sda2(1718)
    -------------------------------------------------------------------------------------------

    Return a list, as shown below:
    [
        {
            'LV'      : 'lv0',
            'VG'      : 'vg0',
            'LSize'   : '52.00m',
            'Region'  : '512.00k',
            'Log'     : 'lv0_mlog',
            'Attr'    : 'mwi-a-m---',
            'Devices' : 'lv0_mimage_0(0),lv0_mimage_1(0)'
        },
        {
            'LV'      : 'lv_root',
            'VG'      : 'vg_test1',
            'LSize'   : '6.71g',
            'Region'  : '0',
            'Attr'    : '-wi-ao----',
            'Devices' : '/dev/sda2(0)'
        }
    ]

    """
    return parse_table(context.content)
