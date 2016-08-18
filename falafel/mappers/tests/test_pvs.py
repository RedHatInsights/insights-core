from falafel.mappers import lvm
from falafel.tests import context_wrap

PVS_INFO = """
LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='500.00m'|LVM2_PV_NAME='/dev/sda1'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '
LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='JvSULk-ileq-JbuS-GGgg-jkif-thuW-zvFBEl'|LVM2_DEV_SIZE='476.45g'|LVM2_PV_NAME='/dev/sda2'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='1020.00k'|LVM2_PE_START='1.00m'|LVM2_PV_SIZE='476.45g'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='476.45g'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='121971'|LVM2_PV_PE_ALLOC_COUNT='121970'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '

""".strip()


def test_pvs():
    pvs_records = lvm.Pvs.parse_context(context_wrap(PVS_INFO))
    assert len(pvs_records.data) == 2
    assert pvs_records.data[1] == {
        'Fmt': 'lvm2',
        'UUID': 'JvSULk-ileq-JbuS-GGgg-jkif-thuW-zvFBEl',
        'PV': '/dev/sda2',
        'PSize': '476.45g',
        'PFree': '4.00m',
        'Attr': 'a--',
        'VG': None
    }
    assert pvs_records.pv("/dev/sda1").get("Attr") == "---"
