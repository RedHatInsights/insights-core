from falafel.mappers.lvm import lvs
from falafel.tests import context_wrap


LVS_INFO = """
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
""".strip()


class TestLVS(object):
    def test_lvs(self):
        lvs_list = lvs(context_wrap(LVS_INFO))
        assert len(lvs_list) == 10
        assert lvs_list[0] == {
            'LV': 'lv0',
            'VG': 'vg0',
            'LSize': '52.00m',
            'Region': '512.00k',
            'Log': 'lv0_mlog',
            'Attr': 'mwi-a-m---',
            'Devices': 'lv0_mimage_0(0),lv0_mimage_1(0)'
        }
