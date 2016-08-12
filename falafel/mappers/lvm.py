from falafel.util import parse_keypair_seperated_by_delim
from falafel.core.plugins import mapper


@mapper('pvs')
def pvs(context):
    """
    The CommandSpec of "pvs" defined as:
    /sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all

    Parse each line in the output of pvs based on the CommandSpec of "pvs" in
    specs.py:
    ---------------- Output sample of pvs ---------------

    LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='500.00m'|LVM2_PV_NAME='/dev/sda1'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='0 '|LVM2_PE_START='0 '|LVM2_PV_SIZE='0 '|LVM2_PV_FREE='0 '|LVM2_PV_USED='0 '|LVM2_PV_ATTR='---'|LVM2_PV_ALLOCATABLE=''|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='0'|LVM2_PV_PE_ALLOC_COUNT='0'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='0'|LVM2_PV_MDA_USED_COUNT='0'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '
    LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='JvSULk-ileq-JbuS-GGgg-jkif-thuW-zvFBEl'|LVM2_DEV_SIZE='476.45g'|LVM2_PV_NAME='/dev/sda2'|LVM2_PV_MDA_FREE='0 '|LVM2_PV_MDA_SIZE='1020.00k'|LVM2_PE_START='1.00m'|LVM2_PV_SIZE='476.45g'|LVM2_PV_FREE='4.00m'|LVM2_PV_USED='476.45g'|LVM2_PV_ATTR='a--'|LVM2_PV_ALLOCATABLE='allocatable'|LVM2_PV_EXPORTED=''|LVM2_PV_MISSING=''|LVM2_PV_PE_COUNT='121971'|LVM2_PV_PE_ALLOC_COUNT='121970'|LVM2_PV_TAGS=''|LVM2_PV_MDA_COUNT='1'|LVM2_PV_MDA_USED_COUNT='1'|LVM2_PV_BA_START='0 '|LVM2_PV_BA_SIZE='0 '

    -----------------------------------------------------

    - Returns a list like:
    [
        {
            'LVM2_PV_FMT'    : '',
            'LVM2_PV_UUID'    : '',
            'LVM2_DEV_SIZE'   : '500.00m',
            ...
        },
        {
            'LVM2_PV_FMT'    : 'lvm2',
            'LVM2_PV_UUID'    : 'JvSULk-ileq-JbuS-GGgg-jkif-thuW-zvFBEl',
            'LVM2_DEV_SIZE'   : '476.45g',
            ...
        }
    ]

    """
    return parse_keypair_seperated_by_delim(context.content)


@mapper('vgs')
def vgs(context):
    """
    The CommandSpec of "vgs" defined as:
    /sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all

    Parse each line in the output of vgs based on the CommandSpec of "vgs" in
    specs.py:
    ---------------- Output sample of vgs ---------------

    LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='YCpusB-LEly-THGL-YXhC-t3q6-mUQV-wyFZrx'|LVM2_VG_NAME='rhel'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='476.45g'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCKTYPE=''|LVM2_VG_LOCKARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='121971'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='4'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='1020.00k'|LVM2_VG_MDA_COPIES='unmanaged'
    LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='123456-LEly-THGL-YXhC-t3q6-mUQV-123456'|LVM2_VG_NAME='fedora'|LVM2_VG_ATTR='wz--n-'|LVM2_VG_PERMISSIONS='writeable'|LVM2_VG_EXTENDABLE='extendable'|LVM2_VG_EXPORTED=''|LVM2_VG_PARTIAL=''|LVM2_VG_ALLOCATION_POLICY='normal'|LVM2_VG_CLUSTERED=''|LVM2_VG_SIZE='476.45g'|LVM2_VG_FREE='4.00m'|LVM2_VG_SYSID=''|LVM2_VG_SYSTEMID=''|LVM2_VG_LOCKTYPE=''|LVM2_VG_LOCKARGS=''|LVM2_VG_EXTENT_SIZE='4.00m'|LVM2_VG_EXTENT_COUNT='121971'|LVM2_VG_FREE_COUNT='1'|LVM2_MAX_LV='0'|LVM2_MAX_PV='0'|LVM2_PV_COUNT='1'|LVM2_LV_COUNT='3'|LVM2_SNAP_COUNT='0'|LVM2_VG_SEQNO='4'|LVM2_VG_TAGS=''|LVM2_VG_PROFILE=''|LVM2_VG_MDA_COUNT='1'|LVM2_VG_MDA_USED_COUNT='1'|LVM2_VG_MDA_FREE='0 '|LVM2_VG_MDA_SIZE='1020.00k'|LVM2_VG_MDA_COPIES='unmanaged'

    -----------------------------------------------------

    - Returns a list like:
    [
        {
            'LVM2_PV_FMT'    : 'lvm2',
            'LVM2_VG_UUID'    : 'YCpusB-LEly-THGL-YXhC-t3q6-mUQV-wyFZrx',
            'LVM2_VG_NAME'   : 'rhel',
            ...
        },
        {
            'LVM2_PV_FMT'    : 'lvm2',
            'LVM2_VG_UUID'    : '123456-LEly-THGL-YXhC-t3q6-mUQV-123456',
            'LVM2_VG_NAME'   : 'fedora',
            ...
        }
    ]

    """
    return parse_keypair_seperated_by_delim(context.content)


@mapper('lvs')
def lvs(context):
    """
    The CommandSpec of "lvs" defined as:
    /sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_all

    Parse each line in the output of lvs based on the CommandSpec of "lvs" in
    specs.py:

    ---------------------------------- Output sample of lvs -----------------------------------
    LVM2_LV_UUID='KX68JI-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m'|LVM2_LV_NAME='docker-poolmeta'|LVM2_LV_FULL_NAME='rhel/docker-poolmeta'|LVM2_LV_PATH='/dev/rhel/docker-poolmeta'|LVM2_LV_DM_PATH='/dev/mapper/rhel-docker--poolmeta'|
    LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-a-----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|
    LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|
    LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='44.00m'|
    LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|
    LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_CONVERT_LV=''|LVM2_MIRROR_LOG=''|
    LVM2_DATA_LV=''|LVM2_METADATA_LV=''|LVM2_POOL_LV=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2016-01-27 14:31:39 +0800'|LVM2_LV_HOST='dhcp-192-57.pek.redhat.com'|LVM2_LV_MODULES=''|
    LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='6'|LVM2_LV_KERNEL_READ_AHEAD='4.00m'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|
    LVM2_LV_DEVICE_OPEN=''|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|
    LVM2_LV_HEALTH_STATUS=''
    LVM2_LV_UUID='123456-8ISN-YedH-ZYDf-yZbK-zkqE-123456'|LVM2_LV_NAME='rhel_root'|LVM2_LV_FULL_NAME='rhel/rhel_root'|LVM2_LV_PATH='/dev/rhel/docker-poolmeta'|LVM2_LV_DM_PATH='/dev/mapper/rhel-docker--poolmeta'|
    LVM2_LV_PARENT=''|LVM2_LV_ATTR='-wi-a-----'|LVM2_LV_LAYOUT='linear'|LVM2_LV_ROLE='public'|LVM2_LV_INITIAL_IMAGE_SYNC=''|LVM2_LV_IMAGE_SYNCED=''|LVM2_LV_MERGING=''|LVM2_LV_CONVERTING=''|LVM2_LV_ALLOCATION_POLICY='inherit'|
    LVM2_LV_ALLOCATION_LOCKED=''|LVM2_LV_FIXED_MINOR=''|LVM2_LV_MERGE_FAILED='unknown'|LVM2_LV_SNAPSHOT_INVALID='unknown'|LVM2_LV_SKIP_ACTIVATION=''|LVM2_LV_WHEN_FULL=''|LVM2_LV_ACTIVE='active'|
    LVM2_LV_ACTIVE_LOCALLY='active locally'|LVM2_LV_ACTIVE_REMOTELY=''|LVM2_LV_ACTIVE_EXCLUSIVELY='active exclusively'|LVM2_LV_MAJOR='-1'|LVM2_LV_MINOR='-1'|LVM2_LV_READ_AHEAD='auto'|LVM2_LV_SIZE='44.00m'|
    LVM2_LV_METADATA_SIZE=''|LVM2_SEG_COUNT='1'|LVM2_ORIGIN=''|LVM2_ORIGIN_SIZE=''|LVM2_LV_ANCESTORS=''|LVM2_LV_DESCENDANTS=''|LVM2_DATA_PERCENT=''|LVM2_SNAP_PERCENT=''|LVM2_METADATA_PERCENT=''|LVM2_COPY_PERCENT=''|
    LVM2_SYNC_PERCENT=''|LVM2_RAID_MISMATCH_COUNT=''|LVM2_RAID_SYNC_ACTION=''|LVM2_RAID_WRITE_BEHIND=''|LVM2_RAID_MIN_RECOVERY_RATE=''|LVM2_RAID_MAX_RECOVERY_RATE=''|LVM2_MOVE_PV=''|LVM2_CONVERT_LV=''|LVM2_MIRROR_LOG=''|
    LVM2_DATA_LV=''|LVM2_METADATA_LV=''|LVM2_POOL_LV=''|LVM2_LV_TAGS=''|LVM2_LV_PROFILE=''|LVM2_LV_LOCKARGS=''|LVM2_LV_TIME='2016-01-27 14:31:39 +0800'|LVM2_LV_HOST='dhcp-192-57.pek.redhat.com'|LVM2_LV_MODULES=''|
    LVM2_LV_KERNEL_MAJOR='253'|LVM2_LV_KERNEL_MINOR='6'|LVM2_LV_KERNEL_READ_AHEAD='4.00m'|LVM2_LV_PERMISSIONS='writeable'|LVM2_LV_SUSPENDED=''|LVM2_LV_LIVE_TABLE='live table present'|LVM2_LV_INACTIVE_TABLE=''|
    LVM2_LV_DEVICE_OPEN=''|LVM2_CACHE_TOTAL_BLOCKS=''|LVM2_CACHE_USED_BLOCKS=''|LVM2_CACHE_DIRTY_BLOCKS=''|LVM2_CACHE_READ_HITS=''|LVM2_CACHE_READ_MISSES=''|LVM2_CACHE_WRITE_HITS=''|LVM2_CACHE_WRITE_MISSES=''|
    LVM2_LV_HEALTH_STATUS=''
    -------------------------------------------------------------------------------------------

    Return a list, as shown below:
    [
        {
            'LVM2_LV_UUID'      : 'KX68JI-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m',
            'LVM2_LV_NAME'      : 'docker-poolmeta',
            'LVM2_LV_FULL_NAME'   : 'rhel/docker-poolmeta',
            ...
        },
        {
            'LVM2_LV_UUID'      : '123456-8ISN-YedH-ZYDf-yZbK-zkqE-123456',
            'LVM2_LV_NAME'      : 'rhel_root',
            'LVM2_LV_FULL_NAME'   : 'rhel/rhel_root',
            ...
        }
    ]

    """
    return parse_keypair_seperated_by_delim(context.content)
