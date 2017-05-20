from falafel.mappers.lvm import Lvs, LvsHeadings, map_keys
from falafel.tests import context_wrap

LVS_INFO = """
  LVM2_LV_UUID='kw1ONN-Su5R-TTxt-G4Vi-ZoRx-KSRd-sG0CJ5'|LVM2_LV_NAME='home'|LVM2_LV_FULL_NAME='fedora_kjl/home'|LVM2_LV_PATH='/dev/fedora_kjl/home'|LVM2_LV_DM_PATH='/dev/mapper/fedora_kjl-home'|LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='182.23g'|LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_UUID=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_MOVE_PV_UUID=''|LVM2_CONVERT_LV=''|LVM2_CONVERT_LV_UUID=''|LVM2_MIRROR_LOG=''|LVM2_MIRROR_LOG_UUID=''|LVM2_DATA_LV=''|LVM2_DATA_LV_UUID=''|LVM2_METADATA_LV=''|LVM2_METADATA_LV_UUID=''|LVM2_POOL_LV=''|LVM2_POOL_LV_UUID=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2015-09-23 21:42:49 -0500'|LVM2_LV_HOST='kjl.me'|LVM2_LV_MODULES=''|LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='3'|LVM2_LV_KERNEL_READ_AHEAD='128.00k'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|LVM2_LV_DEVICE_OPEN='open'|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|LVM2_LV_HEALTH_STATUS=''
    LVM2_LV_UUID='BqPEaY-2mcf-0GOV-Q31u-vGlJ-rm2Z-wG2ABl'|LVM2_LV_NAME='root'|LVM2_LV_FULL_NAME='fedora_kjl/root'|LVM2_LV_PATH='/dev/fedora_kjl/root'|LVM2_LV_DM_PATH='/dev/mapper/fedora_kjl-root'|LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='50.00g'|LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_UUID=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_MOVE_PV_UUID=''|LVM2_CONVERT_LV=''|LVM2_CONVERT_LV_UUID=''|LVM2_MIRROR_LOG=''|LVM2_MIRROR_LOG_UUID=''|LVM2_DATA_LV=''|LVM2_DATA_LV_UUID=''|LVM2_METADATA_LV=''|LVM2_METADATA_LV_UUID=''|LVM2_POOL_LV=''|LVM2_POOL_LV_UUID=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2015-09-23 21:42:52 -0500'|LVM2_LV_HOST='kjl.me'|LVM2_LV_MODULES=''|LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='2'|LVM2_LV_KERNEL_READ_AHEAD='128.00k'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|LVM2_LV_DEVICE_OPEN='open'|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|LVM2_LV_HEALTH_STATUS=''
      LVM2_LV_UUID='27XoiT-2R2d-jcgv-pVNw-LqBO-tKIB-6eHpFn'|LVM2_LV_NAME='swap'|LVM2_LV_FULL_NAME='fedora_kjl/swap'|LVM2_LV_PATH='/dev/fedora_kjl/swap'|LVM2_LV_DM_PATH='/dev/mapper/fedora_kjl-swap'|LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='5.75g'|LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_UUID=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_MOVE_PV_UUID=''|LVM2_CONVERT_LV=''|LVM2_CONVERT_LV_UUID=''|LVM2_MIRROR_LOG=''|LVM2_MIRROR_LOG_UUID=''|LVM2_DATA_LV=''|LVM2_DATA_LV_UUID=''|LVM2_METADATA_LV=''|LVM2_METADATA_LV_UUID=''|LVM2_POOL_LV=''|LVM2_POOL_LV_UUID=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2015-09-23 21:42:49 -0500'|LVM2_LV_HOST='kjl.me'|LVM2_LV_MODULES=''|LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='1'|LVM2_LV_KERNEL_READ_AHEAD='128.00k'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|LVM2_LV_DEVICE_OPEN='open'|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|LVM2_LV_HEALTH_STATUS=''
""".strip()

LVS_ROOT_INFO = {
    "MergeFailed": "unknown",
    "#Seg": "1",
    "Ancestors": "",
    "Layout": "linear",
    "Meta%": "",
    "LPerms": "writeable",
    "Data%": "",
    "AllocLock": "",
    "Health": "",
    "CacheDirtyBlocks": "",
    "CacheWriteMisses": "",
    "MaxSync": "",
    "Pool_UUID": "",
    "Data_UUID": "",
    "DMPath": "/dev/mapper/fedora_kjl-root",
    "CacheTotalBlocks": "",
    "Log": "",
    "SkipAct": "",
    "Min": "-1",
    "Mismatches": "",
    "SyncAction": "",
    "WBehind": "",
    "ActExcl": "active exclusively",
    "Parent": "",
    "ActRemote": "",
    "OSize": "",
    "WhenFull": "",
    "Log_UUID": "",
    "KMin": "2",
    "Lock_Args": "",
    "LV": "root",
    "CacheReadMisses": "",
    "Host": "kjl.me",
    "CacheWriteHits": "",
    "DevOpen": "open",
    "InitImgSync": "",
    "Active": "active",
    "Path": "/dev/fedora_kjl/root",
    "Move_UUID": "",
    "Maj": "-1",
    "Data": "",
    "LV_Tags": "",
    "Pool": "",
    "KMaj": "253",
    "Convert": "",
    "LProfile": "",
    "AllocPol": "inherit",
    "Attr": "-wi-ao----",
    "VG": None,
    "KRahead": "128.00k",
    "LiveTable": "live table present",
    "Modules": "",
    "Meta_UUID": "",
    "Devices": None,
    "MSize": "",
    "Merging": "",
    "Descendants": "",
    "ActLocal": "active locally",
    "Time": "2015-09-23 21:42:52 -0500",
    "Cpy%Sync": "",
    "LV_UUID": "BqPEaY-2mcf-0GOV-Q31u-vGlJ-rm2Z-wG2ABl",
    "Origin": "",
    "MinSync": "",
    "Converting": "",
    "SnapInvalid": "unknown",
    "ImgSynced": "",
    "Move": "",
    "CacheReadHits": "",
    "Origin_UUID": "",
    "Snap%": "",
    "Meta": "",
    "InactiveTable": "",
    "FixMin": "",
    "Suspended": "",
    "Rahead": "auto",
    "CacheUsedBlocks": "",
    "Role": "public",
    "LSize": "50.00g",
    "Region": None
}


# There is some non-realistic data in the sample below for testing purposes
LVS_HEADER_1 = """
  WARNING: Locking disabled. Be careful! This could corrupt your metadata.
  LV          VG      Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert LV Tags Devices        
  lv_app      vg_root -wi-ao---- 71.63g                                    C      c                 /dev/sda2(7136)
  lv_home     vg_root -wi-ao----  2.00g                                L g                          /dev/sda2(2272)
  lv_opt      vg_root -wi-ao----  5.00g                           M  e                              /dev/sda2(2784)
  lv_root     vg_root -wi-ao----  5.00g P  l O    n D   %  M   %                                    /dev/sda2(0)   
  lv_tmp      vg_root -wi-ao----  1.00g                                             C     t         /dev/sda2(4064)
  lv_usr      vg_root -wi-ao----  5.00g                                                     L     s /dev/sda2(4320)
  lv_usrlocal vg_root -wi-ao----  1.00g                                                             /dev/sda2(5600)
  lv_var      vg_root -wi-ao----  5.00g                                                             /dev/sda2(5856)
  swap        vg_root -wi-ao----  3.88g                                                             /dev/sda2(1280)
""".strip()  # noqa: W291

LVS_HEADER_BYKEY = [
    {
        'Origin': '',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(7136)',
        'LV_Tags': '',
        'LV': 'lv_app',
        'LSize': '71.63g',
        'Cpy%Sync': 'C      c',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': '',
        'Convert': '',
        'Log': 'L g',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(2272)',
        'LV_Tags': '',
        'LV': 'lv_home',
        'LSize': '2.00g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': '',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': 'M  e',
        'Devices': '/dev/sda2(2784)',
        'LV_Tags': '',
        'LV': 'lv_opt',
        'LSize': '5.00g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': 'O    n',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': 'D   %',
        'Move': '',
        'Devices': '/dev/sda2(0)',
        'LV_Tags': '',
        'LV': 'lv_root',
        'LSize': '5.00g',
        'Cpy%Sync': '',
        'Pool': 'P  l',
        'Meta%': 'M   %'
    }, {
        'Origin': '',
        'Convert': 'C     t',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(4064)',
        'LV_Tags': '',
        'LV': 'lv_tmp',
        'LSize': '1.00g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': '',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(4320)',
        'LV_Tags': 'L     s',
        'LV': 'lv_usr',
        'LSize': '5.00g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': '',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(5600)',
        'LV_Tags': '',
        'LV': 'lv_usrlocal',
        'LSize': '1.00g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': '',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(5856)',
        'LV_Tags': '',
        'LV': 'lv_var',
        'LSize': '5.00g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }, {
        'Origin': '',
        'Convert': '',
        'Log': '',
        'Attr': '-wi-ao----',
        'VG': 'vg_root',
        'Data%': '',
        'Move': '',
        'Devices': '/dev/sda2(1280)',
        'LV_Tags': '',
        'LV': 'swap',
        'LSize': '3.88g',
        'Cpy%Sync': '',
        'Pool': '',
        'Meta%': ''
    }
]


class TestLVS(object):
    def test_lvs(self):
        lvs_list = Lvs(context_wrap(LVS_INFO))
        assert len(lvs_list) == 3
        for k, v in LVS_ROOT_INFO.iteritems():
            assert lvs_list.data["content"][1][k] == v
        assert lvs_list["swap"]["LSize"] == "5.75g"
        assert lvs_list.data['content'][1]['LVM2_LV_DEVICE_OPEN'] == 'open'

    def test_map_keys(self):
        pvs = [{'LVM2_LV_NAME': 'lv1'}]
        name = self._get_value_after_map_keys(pvs, 'LV')
        assert name == 'lv1'

        pvs = [{'LVM2_LV_FULL_NAME': 'lv1'}]
        name = self._get_value_after_map_keys(pvs, 'LV')
        assert name == 'lv1'

    def _get_value_after_map_keys(self, pvs, key):
        pvs = map_keys(pvs, Lvs.KEYS)
        for pv in pvs:
            return pv[key]


def test_lvs_headers():
    lvs_info = LvsHeadings(context_wrap(LVS_HEADER_1))
    assert lvs_info is not None
    for l in range(len(LVS_HEADER_BYKEY)):
        for k, v in LVS_HEADER_BYKEY[l].iteritems():
            assert lvs_info.data[l][k] == v
