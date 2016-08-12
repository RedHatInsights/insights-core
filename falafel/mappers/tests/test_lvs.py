from falafel.mappers.lvm import lvs
from falafel.tests import context_wrap

LVS_INFO = """
LVM2_LV_UUID='KX68JI-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m'|LVM2_LV_NAME='docker-poolmeta'|LVM2_LV_FULL_NAME='rhel/docker-poolmeta'|LVM2_LV_PATH='/dev/rhel/docker-poolmeta'|LVM2_LV_DM_PATH='/dev/mapper/rhel-docker--poolmeta'|LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-a-----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='44.00m'|LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_CONVERT_LV=''|LVM2_MIRROR_LOG=''|LVM2_DATA_LV=''|LVM2_METADATA_LV=''|LVM2_POOL_LV=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2016-01-27 14:31:39 +0800'|LVM2_LV_HOST='dhcp-192-57.pek.redhat.com'|LVM2_LV_MODULES=''|LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='6'|LVM2_LV_KERNEL_READ_AHEAD='4.00m'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|LVM2_LV_DEVICE_OPEN=''|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|LVM2_LV_HEALTH_STATUS=''
LVM2_LV_UUID='123456-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m'|LVM2_LV_NAME='docker-poolmeta'|LVM2_LV_FULL_NAME='rhel/test_root'|LVM2_LV_PATH='/dev/rhel/docker-poolmeta'|LVM2_LV_DM_PATH='/dev/mapper/rhel-docker--poolmeta'|LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-a-----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='44.00m'|LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_CONVERT_LV=''|LVM2_MIRROR_LOG=''|LVM2_DATA_LV=''|LVM2_METADATA_LV=''|LVM2_POOL_LV=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2016-01-27 14:31:39 +0800'|LVM2_LV_HOST='dhcp-192-57.pek.redhat.com'|LVM2_LV_MODULES=''|LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='6'|LVM2_LV_KERNEL_READ_AHEAD='4.00m'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|LVM2_LV_DEVICE_OPEN=''|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|LVM2_LV_HEALTH_STATUS=''

""".strip()


class TestLVS(object):
    def test_lvs(self):
        lvs_list = lvs(context_wrap(LVS_INFO))
        assert len(lvs_list) == 2
        assert lvs_list[1] == {
            'LVM2_LV_UUID': '123456-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m',
            'LVM2_LV_NAME': 'docker-poolmeta',
            'LVM2_LV_FULL_NAME': 'rhel/test_root',
            'LVM2_LV_PATH': '/dev/rhel/docker-poolmeta',
            'LVM2_LV_PARENT': '',
            'LVM2_LV_DM_PATH': '/dev/mapper/rhel-docker--poolmeta',
            'LVM2_LV_ATTR': '-wi-a-----',
            'LVM2_LV_LAYOUT': 'linear',
            'LVM2_LV_ROLE': 'public',
            'LVM2_LV_INITIAL_IMAGE_SYNC': '',
            'LVM2_LV_IMAGE_SYNCED': '',
            'LVM2_LV_MERGING': '',
            'LVM2_LV_CONVERTING': '',
            'LVM2_LV_ALLOCATION_POLICY': 'inherit',
            'LVM2_LV_ALLOCATION_LOCKED': '',
            'LVM2_LV_FIXED_MINOR': '',
            'LVM2_LV_MERGE_FAILED': 'unknown',
            'LVM2_LV_SNAPSHOT_INVALID': 'unknown',
            'LVM2_LV_SKIP_ACTIVATION': '',
            'LVM2_LV_WHEN_FULL': '',
            'LVM2_LV_ACTIVE': 'active',
            'LVM2_LV_ACTIVE_LOCALLY': 'active locally',
            'LVM2_LV_ACTIVE_REMOTELY': '',
            'LVM2_LV_ACTIVE_EXCLUSIVELY': 'active exclusively',
            'LVM2_LV_MAJOR': '-1',
            'LVM2_LV_MINOR': '-1',
            'LVM2_LV_READ_AHEAD': 'auto',
            'LVM2_LV_SIZE': '44.00m',
            'LVM2_LV_METADATA_SIZE': '',
            'LVM2_SEG_COUNT': '1',
            'LVM2_ORIGIN': '',
            'LVM2_ORIGIN_SIZE': '',
            'LVM2_LV_ANCESTORS': '',
            'LVM2_LV_DESCENDANTS': '',
            'LVM2_DATA_PERCENT': '',
            'LVM2_SNAP_PERCENT': '',
            'LVM2_METADATA_PERCENT': '',
            'LVM2_COPY_PERCENT': '',
            'LVM2_SYNC_PERCENT': '',
            'LVM2_RAID_MISMATCH_COUNT': '',
            'LVM2_RAID_SYNC_ACTION': '',
            'LVM2_RAID_WRITE_BEHIND': '',
            'LVM2_RAID_MIN_RECOVERY_RATE': '',
            'LVM2_RAID_MAX_RECOVERY_RATE': '',
            'LVM2_MOVE_PV': '',
            'LVM2_CONVERT_LV': '',
            'LVM2_MIRROR_LOG': '',
            'LVM2_DATA_LV': '',
            'LVM2_METADATA_LV': '',
            'LVM2_POOL_LV': '',
            'LVM2_LV_TAGS': '',
            'LVM2_LV_PROFILE': '',
            'LVM2_LV_LOCKARGS': '',
            'LVM2_LV_TIME': '2016-01-27 14:31:39 +0800',
            'LVM2_LV_HOST': 'dhcp-192-57.pek.redhat.com',
            'LVM2_LV_MODULES': '',
            'LVM2_LV_KERNEL_MAJOR': '253',
            'LVM2_LV_KERNEL_MINOR': '6',
            'LVM2_LV_KERNEL_READ_AHEAD': '4.00m',
            'LVM2_LV_PERMISSIONS': 'writeable',
            'LVM2_LV_SUSPENDED': '',
            'LVM2_LV_LIVE_TABLE': 'live table present',
            'LVM2_LV_INACTIVE_TABLE': '',
            'LVM2_LV_DEVICE_OPEN': '',
            'LVM2_CACHE_TOTAL_BLOCKS': '',
            'LVM2_CACHE_USED_BLOCKS': '',
            'LVM2_CACHE_DIRTY_BLOCKS': '',
            'LVM2_CACHE_READ_HITS': '',
            'LVM2_CACHE_READ_MISSES': '',
            'LVM2_CACHE_WRITE_HITS': '',
            'LVM2_CACHE_WRITE_MISSES': '',
            'LVM2_LV_HEALTH_STATUS': ''
        }
        assert lvs_list[0].get("LVM2_LV_UUID") == "KX68JI-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m"
        assert lvs_list[0].get("LVM2_LV_FULL_NAME") == 'rhel/docker-poolmeta'
