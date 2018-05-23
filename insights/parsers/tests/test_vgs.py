from insights.parsers.lvm import Vgs, VgsHeadings
from insights.tests import context_wrap

VGS_INFO = """
LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='YCpusB-LEly-THGL-YXhC-t3q6-mUQV-wyFZrx'|LVM2_VG_NAME='rhel'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='476.45g'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCKTYPE=''|LVM2_VG_LOCKARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='121971'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='4'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='1020.00k'|LVM2_VG_MDA_COPIES='unmanaged'
LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='123456-LEly-THGL-YXhC-t3q6-mUQV-123456'|LVM2_VG_NAME='fedora'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='476.45g'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCKTYPE=''|LVM2_VG_LOCKARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='121971'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='4'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='1020.00k'|LVM2_VG_MDA_COPIES='unmanaged'

""".strip()

VGS_INFO_FEDORA = {
    'VG': 'fedora',
    'Attr': 'wz--n-',
    'VSize': '476.45g',
    'VFree': '4.00m',
    '#PV': '1',
    '#LV': '3',
    '#SN': '0',
    '#Ext': '121971',
    '#VMda': '1',
    '#VMdaCps': 'unmanaged',
    '#VMdaUse': '1',
    'AllocPol': 'normal',
    'Clustered': '',
    'Exported': '',
    'Ext': '4.00m',
    'Extendable': 'extendable',
    'Fmt': 'lvm2',
    'Free': '1',
    'Lock Args': '',
    'Lock_Type': '',
    'MaxLV': '0',
    'MaxPV': '0',
    'Partial': '',
    'SYS_ID': '',
    'Seq': '4',
    'System_ID': '',
    'VG_Tags': '',
    'VG_UUID': '123456-LEly-THGL-YXhC-t3q6-mUQV-123456',
    'VMdaFree': '0',
    'VMdaSize': '1020.00k',
    'VPerms': 'writeable',
    'VProfile': ''
}

VGS_HEADER_INFO = """
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
""".strip()   # noqa: W291

VGS_HEADER_5 = {
    'VG': 'rootvg',
    'Attr': 'wz--n-',
    'Ext': '4.00m',
    '#PV': '1',
    '#LV': '6',
    '#SN': '0',
    'VSize': '19.51g',
    'VFree': '1.95g',
    'VG_UUID': 'p4tLLb-ikeo-Ankk-2xJ6-iHYf-D4E6-KFCFvr',
    'VProfile': '',
    '#VMda': '1',
    'VMdaFree': '506.50k',
    'VMdaSize': '1020.00k',
    '#VMdaUse': '1',
    'VG_Tags': ''
}


def test_vgs():
    vgs_records = Vgs(context_wrap(VGS_INFO))
    assert len(list(vgs_records)) == 2
    for k, v in VGS_INFO_FEDORA.items():
        assert vgs_records["fedora"][k] == v
    assert vgs_records["fedora"]['LVM2_VG_SEQNO'] == '4'


def test_vgs_headers():
    vgs_info = VgsHeadings(context_wrap(VGS_HEADER_INFO))
    assert vgs_info is not None
    assert len(vgs_info.data) == 6
    for k, v in VGS_HEADER_5.items():
        assert vgs_info[5][k] == v
    assert vgs_info[5]['VPerms'] is None
