from falafel.mappers.lvm import Lvs
from falafel.tests import context_wrap

LVS_INFO = """
  LVM2_LV_NAME='home'|LVM2_VG_NAME='fedora_kjl'|LVM2_LV_SIZE='182.23g'|LVM2_REGIONSIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/mapper/luks-2c4fc590-db3c-4099-9b9a-51372deef87c(1472)'
  LVM2_LV_NAME='root'|LVM2_VG_NAME='fedora_kjl'|LVM2_LV_SIZE='50.00g'|LVM2_REGIONSIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/mapper/luks-2c4fc590-db3c-4099-9b9a-51372deef87c(48122)'
  LVM2_LV_NAME='swap'|LVM2_VG_NAME='fedora_kjl'|LVM2_LV_SIZE='5.75g'|LVM2_REGIONSIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/mapper/luks-2c4fc590-db3c-4099-9b9a-51372deef87c(0)'
""".strip()


class TestLVS(object):
    def test_lvs(self):
        lvs_list = Lvs.parse_context(context_wrap(LVS_INFO))
        assert len(lvs_list.data) == 3
        assert lvs_list.data[1] == {
            "LV": "root",
            "VG": "fedora_kjl",
            "LSize": "50.00g",
            "Region": "0",
            "Log": "",
            "Attr": "-wi-ao----",
            "Devices": "/dev/mapper/luks-2c4fc590-db3c-4099-9b9a-51372deef87c(48122)"
        }
        assert lvs_list.lv("swap").get("LSize") == "5.75g"
