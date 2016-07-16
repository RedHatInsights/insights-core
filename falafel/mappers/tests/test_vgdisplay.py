from falafel.mappers import vgdisplay
from falafel.tests import context_wrap


VGDISPLAY = """
Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV.
  There are 1 physical volumes missing.
    Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV.
  There are 1 physical volumes missing.
--- Volume group ---
VG Name               rhel_hp-dl160g8-3
Format                lvm2
System ID
Metadata Areas        1
Metadata Sequence No  5
VG Access             read/write
Total PE              119109
Alloc PE / Size       119098 / 465.23 GiB
Free  PE / Size       11 / 44.00 MiB
VG UUID               by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZD

VG Name               rhel_hp-dl260g7-4
Format                lvm2
System ID
VG Access             read/write
Alloc PE / Size       119098 / 465.23 GiB
Free  PE / Size       11 / 44.00 MiB
VG UUID               by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZN
""".strip()


class TestVGdisplay():
    def test_vgdisplay(self):
        vg_info = vgdisplay.get_vginfo(context_wrap(VGDISPLAY))
        assert len(vg_info) == 2
        assert vg_info['vginfo_dict'][0].get('VG Name') == 'rhel_hp-dl160g8-3'
        assert vg_info['vginfo_dict'][1].get('VG UUID') == 'by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZN'
        assert vg_info['debug_info'][0] == "Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV."
        assert vg_info['debug_info'][1] == "There are 1 physical volumes missing."
