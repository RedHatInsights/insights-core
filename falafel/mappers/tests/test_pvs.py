from falafel.mappers import lvm
from falafel.tests import context_wrap

PVS_INFO = """
PV         VG                Fmt  Attr PSize   PFree
/dev/sda2  rhel_hp-dl160g8-3 lvm2 a--  465.27g 44.00m
/dev/sda3  rhel_hp-dl180g8-4 lvm2 a--  200.18g 40.00m
""".strip()


def test_pvs():
    pvs_records = lvm.pvs(context_wrap(PVS_INFO))
    assert len(pvs_records) == 2
    assert pvs_records[0] == {
        'PV': '/dev/sda2',
        'VG': 'rhel_hp-dl160g8-3',
        'Fmt': 'lvm2',
        'Attr': 'a--',
        'PSize': '465.27g',
        'PFree': '44.00m'
    }
    assert pvs_records[1] == {
        'PV': '/dev/sda3',
        'VG': 'rhel_hp-dl180g8-4',
        'Fmt': 'lvm2',
        'Attr': 'a--',
        'PSize': '200.18g',
        'PFree': '40.00m'
    }
