import json
from ..util import parse_keypair_lines
from .. import Mapper, mapper, parse_table, get_active_lines, LegacyItemAccess


def map_keys(pvs, keys):
    rs = []
    for pv in pvs:
        r = {v: None for k, v in keys.iteritems()}
        for k, v in pv.iteritems():
            if k in keys:
                r[keys[k]] = v
        rs.append(r)
    return rs


def replace_spaces_in_keys(header):
    for k in KEYS_WITH_SPACES:
        if k in header:
            header = header.replace(k, k.replace(" ", "_"))
    return header


def find_warnings(content):
    keywords = [k.lower() for k in [
        "WARNING", "Couldn't find device", "Configuration setting",
        "read failed", "Was device resized?", "Invalid argument",
        "leaked on lvs", "Checksum error", "is exported", "failed.",
        "Invalid metadata", "response failed", "unknown device",
        "duplicate", "not found", "Missing device", "Internal error",
        "Input/output error", "Incorrect metadata", "Cannot process volume",
        "No such file or directory", "Logging initialised", "changed sizes",
        "vsnprintf failed", "write failed", "correction failed",
        "Failed to write", "Couldn't read", "marked missing",
        "Attempt to close device", "Ignoring supplied major",
        "not match metadata"
    ]]
    for l in content:
        lower = l.strip().lower()
        if any(k in lower for k in keywords):
            yield l


class Lvm(Mapper):

    def parse_content(self, content):
        d = {"warnings": set(find_warnings(content))}
        content = [l for l in content if l not in d["warnings"]]
        try:
            d["content"] = list(map_keys(parse_keypair_lines(content), self.KEYS))
        except:
            content[0] = replace_spaces_in_keys(content[0])
            d["content"] = parse_table(content)
        self.data = d if d else None

    def __iter__(self):
        return iter(self.data["content"])

    def __len__(self):
        return len(self.data["content"])

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data["content"][key]
        i = [i for i in self.data["content"] if i[self.PRIMARY_KEY] == key]
        return i[0] if len(i) > 0 else self.computed[key]

    @property
    def locking_disabled(self):
        return len([l for l in self.data["warnings"] if "Locking disabled" in l]) > 0

    @property
    def warnings(self):
        return self.data["warnings"]


@mapper('pvs')
@mapper('pvs_noheadings')
class Pvs(Lvm):
    """
    The CommandSpec of "pvs" defined as:
    /sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all

    Parse each line in the output of pvs based on the CommandSpec of "pvs" in
    specs.py:
    ---------------- Output sample of pvs ---------------

    LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='500.00m'|...
    LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='JvSULk-ileq-JbuS-GGgg-jkif-thuW-zvFBEl'|LVM2_DEV_SIZE='476.45g'|...

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
    KEYS = {
        "LVM2_PV_MDA_USED_COUNT": "#PMdaUse",
        "LVM2_PV_UUID": "PV_UUID",
        "LVM2_DEV_SIZE": "DevSize",
        "LVM2_PV_FMT": "Fmt",
        "LVM2_PV_MDA_FREE": "PMdaFree",
        "LVM2_PV_EXPORTED": "Exported",
        "LVM2_PV_SIZE": "PSize",
        "LVM2_PV_BA_START": "BA_start",
        "LVM2_PV_PE_ALLOC_COUNT": "Alloc",
        "LVM2_VG_NAME": "VG",
        "LVM2_PV_TAGS": "PV_Tags",
        "LVM2_PV_PE_COUNT": "PE",
        "LVM2_PV_BA_SIZE": "BA_size",
        "LVM2_PV_ATTR": "Attr",
        "LVM2_PE_START": "1st_PE",
        "LVM2_PV_USED": "Used",
        "LVM2_PV_NAME": "PV",
        "LVM2_PV_MDA_COUNT": "#PMda",
        "LVM2_PV_FREE": "PFree",
        "LVM2_PV_ALLOCATABLE": "Allocatable",
        "LVM2_PV_MDA_SIZE": "PMdaSize",
        "LVM2_PV_MISSING": "Missing"
    }

    PRIMARY_KEY = "PV"

    def vg(self, name):
        """Return all physical volumes assigned to the given volume group"""
        return [i for i in self.data["content"] if i["VG"] == name]


@mapper('vgs')
@mapper('vgs_noheadings')
class Vgs(Lvm):
    """
    The CommandSpec of "vgs" defined as:
    /sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all

    Parse each line in the output of vgs based on the CommandSpec of "vgs" in
    specs.py:
    ---------------- Output sample of vgs ---------------

    LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='YCpusB-LEly-THGL-YXhC-t3q6-mUQV-wyFZrx'|LVM2_VG_NAME='rhel'|LVM2_VG_ATTR='wz--n-'|...
    LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='123456-LEly-THGL-YXhC-t3q6-mUQV-123456'|LVM2_VG_NAME='fedora'|LVM2_VG_ATTR='wz--n-'|...

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
    KEYS = {
        "LVM2_VG_EXTENDABLE": "Extendable",
        "LVM2_VG_EXTENT_SIZE": "Ext",
        "LVM2_VG_MDA_COUNT": "#VMda",
        "LVM2_VG_PROFILE": "VProfile",
        "LVM2_VG_ALLOCATION_POLICY": "AllocPol",
        "LVM2_MAX_PV": "MaxPV",
        "LVM2_VG_UUID": "VG_UUID",
        "LVM2_VG_ATTR": "Attr",
        "LVM2_VG_SYSID": "SYS_ID",
        "LVM2_VG_MDA_USED_COUNT": "#VMdaUse",
        "LVM2_VG_MDA_FREE": "VMdaFree",
        "LVM2_VG_LOCKTYPE": "Lock_Type",
        "LVM2_VG_TAGS": "VG_Tags",
        "LVM2_VG_FMT": "Fmt",
        "LVM2_PV_COUNT": "#PV",
        "LVM2_VG_EXTENT_COUNT": "#Ext",
        "LVM2_VG_MDA_SIZE": "VMdaSize",
        "LVM2_SNAP_COUNT": "#SN",
        "LVM2_VG_EXPORTED": "Exported",
        "LVM2_LV_COUNT": "#LV",
        "LVM2_VG_NAME": "VG",
        "LVM2_VG_MDA_COPIES": "#VMdaCps",
        "LVM2_VG_SYSTEMID": "System_ID",
        "LVM2_VG_FREE": "VFree",
        "LVM2_VG_SEQNO": "Seq",
        "LVM2_VG_FREE_COUNT": "Free",
        "LVM2_VG_PARTIAL": "Partial",
        "LVM2_VG_PERMISSIONS": "VPerms",
        "LVM2_VG_CLUSTERED": "Clustered",
        "LVM2_VG_LOCKARGS": "Lock Args",
        "LVM2_MAX_LV": "MaxLV",
        "LVM2_VG_SIZE": "VSize"
    }

    PRIMARY_KEY = "VG"


@mapper('lvs')
@mapper('lvs_noheadings')
class Lvs(Lvm):
    """
    The CommandSpec of "lvs" defined as:
    /sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_all

    Parse each line in the output of lvs based on the CommandSpec of "lvs" in
    specs.py:

    ---------------------------------- Output sample of lvs -----------------------------------

    LVM2_LV_UUID='KX68JI-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m'|LVM2_LV_NAME='docker-poolmeta'|LVM2_LV_FULL_NAME='rhel/docker-poolmeta'|...
    LVM2_LV_UUID='123456-8ISN-YedH-ZYDf-yZbK-zkqE-123456'|LVM2_LV_NAME='rhel_root'|LVM2_LV_FULL_NAME='rhel/rhel_root'|LVM2_LV_PATH='/dev/rhel/docker-poolmeta'|...

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
    KEYS = {
        "LVM2_POOL_LV_UUID": "Pool_UUID",
        "LVM2_LV_PARENT": "Parent",
        "LVM2_LV_SKIP_ACTIVATION": "SkipAct",
        "LVM2_LV_HEALTH_STATUS": "Health",
        "LVM2_LV_KERNEL_MINOR": "KMin",
        "LVM2_RAID_WRITE_BEHIND": "WBehind",
        "LVM2_LV_ANCESTORS": "Ancestors",
        "LVM2_LV_TIME": "Time",
        "LVM2_METADATA_PERCENT": "Meta%",
        "LVM2_LV_DM_PATH": "DMPath",
        "LVM2_LV_INACTIVE_TABLE": "InactiveTable",
        "LVM2_LV_UUID": "LV_UUID",
        "LVM2_LV_MODULES": "Modules",
        "LVM2_DEVICES": "Devices",
        "LVM2_LV_ACTIVE_REMOTELY": "ActRemote",
        "LVM2_LV_ACTIVE_LOCALLY": "ActLocal",
        "LVM2_LV_TAGS": "LV_Tags",
        "LVM2_LV_IMAGE_SYNCED": "ImgSynced",
        "LVM2_CACHE_WRITE_MISSES": "CacheWriteMisses",
        "LVM2_LV_PERMISSIONS": "LPerms",
        "LVM2_CACHE_TOTAL_BLOCKS": "CacheTotalBlocks",
        "LVM2_LV_ACTIVE_EXCLUSIVELY": "ActExcl",
        "LVM2_LV_PATH": "Path",
        "LVM2_LV_FULL_NAME": "LV",
        "LVM2_LV_READ_AHEAD": "Rahead",
        "LVM2_SNAP_PERCENT": "Snap%",
        "LVM2_CACHE_WRITE_HITS": "CacheWriteHits",
        "LVM2_MIRROR_LOG": "Log",
        "LVM2_CACHE_DIRTY_BLOCKS": "CacheDirtyBlocks",
        "LVM2_SEG_COUNT": "#Seg",
        "LVM2_MOVE_PV": "Move",
        "LVM2_LV_FIXED_MINOR": "FixMin",
        "LVM2_SYNC_PERCENT": "Cpy%Sync",
        "LVM2_LV_METADATA_SIZE": "MSize",
        "LVM2_LV_ATTR": "Attr",
        "LVM2_RAID_MAX_RECOVERY_RATE": "MaxSync",
        "LVM2_LV_DEVICE_OPEN": "DevOpen",
        "LVM2_LV_ALLOCATION_POLICY": "AllocPol",
        "LVM2_LV_MERGING": "Merging",
        "LVM2_LV_SIZE": "LSize",
        "LVM2_LV_MAJOR": "Maj",
        "LVM2_ORIGIN_SIZE": "OSize",
        "LVM2_RAID_SYNC_ACTION": "SyncAction",
        "LVM2_MIRROR_LOG_UUID": "Log_UUID",
        "LVM2_POOL_LV": "Pool",
        "LVM2_COPY_PERCENT": "Cpy%Sync",
        "LVM2_CONVERT_LV": "Convert",
        "LVM2_LV_KERNEL_READ_AHEAD": "KRahead",
        "LVM2_LV_NAME": "LV",
        "LVM2_LV_HOST": "Host",
        "LVM2_CACHE_USED_BLOCKS": "CacheUsedBlocks",
        "LVM2_RAID_MIN_RECOVERY_RATE": "MinSync",
        "LVM2_ORIGIN_UUID": "Origin_UUID",
        "LVM2_LV_SUSPENDED": "Suspended",
        "LVM2_RAID_MISMATCH_COUNT": "Mismatches",
        "LVM2_LV_KERNEL_MAJOR": "KMaj",
        "LVM2_LV_LAYOUT": "Layout",
        "LVM2_LV_PROFILE": "LProfile",
        "LVM2_LV_LIVE_TABLE": "LiveTable",
        "LVM2_LV_INITIAL_IMAGE_SYNC": "InitImgSync",
        "LVM2_LV_CONVERTING": "Converting",
        "LVM2_CACHE_READ_HITS": "CacheReadHits",
        "LVM2_VG_NAME": "VG",
        "LVM2_METADATA_LV": "Meta",
        "LVM2_LV_ACTIVE": "Active",
        "LVM2_CONVERT_LV_UUID": "Convert",
        "LVM2_LV_MERGE_FAILED": "MergeFailed",
        "LVM2_METADATA_LV_UUID": "Meta_UUID",
        "LVM2_LV_ROLE": "Role",
        "LVM2_LV_WHEN_FULL": "WhenFull",
        "LVM2_LV_ALLOCATION_LOCKED": "AllocLock",
        "LVM2_DATA_PERCENT": "Data%",
        "LVM2_LV_LOCKARGS": "Lock_Args",
        "LVM2_LV_SNAPSHOT_INVALID": "SnapInvalid",
        "LVM2_MOVE_PV_UUID": "Move_UUID",
        "LVM2_LV_MINOR": "Min",
        "LVM2_ORIGIN": "Origin",
        "LVM2_DATA_LV_UUID": "Data_UUID",
        "LVM2_DATA_LV": "Data",
        "LVM2_CACHE_READ_MISSES": "CacheReadMisses",
        "LVM2_LV_DESCENDANTS": "Descendants",
        "LVM2_REGIONSIZE": "Region"
    }

    PRIMARY_KEY = "LV"

    def parse_content(self, content):
        super(Lvs, self).parse_content(content)
        for item in self.data["content"]:
            lv_name = item["LV"]
            if "/" in lv_name:
                # Reduce full name to just the name
                # This is due to the lvs command having *two identical keys*
                # with different values
                item["LV"] = lv_name.split("/")[1]

    def vg(self, name):
        """Return all logical volumes in the given volume group"""
        return [i for i in self.data["content"] if i["VG"] == name]


KEYS_WITH_SPACES = []
for cls in (Lvs, Pvs, Vgs):
    KEYS_WITH_SPACES.extend([k for k in cls.KEYS.values() if " " in k])


LVM_CONF_FILTERS = [
    "locking_type",  # CMIRROR_PERF_ISSUE
    "filter",  # LVM_CONF_REMOVE_BOOTDEV HA_LVM_RELOCATE_ISSUE LVM_FILTER_ISSUE
    "volume_list"  # HA_LVM_RELOCATE_ISSUE
]


@mapper('lvm.conf', LVM_CONF_FILTERS)
class LvmConf(LegacyItemAccess, Mapper):

    def parse_content(self, content):
        """
        Returns a dict:
        locking_type : 1
        filter : ['a/sda[0-9]*$/', 'r/sd.*/']
        volume_list : ['vg2', 'vg3/lvol3', '@tag2', '@*']
        """
        lvm_conf_dict = {}
        for line in get_active_lines(content):
            if "=" in line:
                (key, value) = [item.strip() for item in line.split('=', 1)]
                try:
                    lvm_conf_dict[key] = json.loads(value)
                except Exception:
                    lvm_conf_dict[key] = value
        self.data = lvm_conf_dict


if __name__ == "__main__":
    # This is a quick script to generate the key mappings in each subclass.
    # Run each lvm command with --separator="|", --nameprefixes and *not* --noheadings

    import sys
    from collections import OrderedDict

    content = sys.stdin.read().splitlines()
    headers = [h.strip().replace(" ", "_") for h in content[0].split("|")]
    nameprefixes = [v.split("=")[0].strip() for v in content[1].replace("0 ", "0").split("|")]
    pairs = zip(nameprefixes, headers)
    print json.dumps(OrderedDict(sorted(pairs, cmp=lambda x, y: cmp(x[0], y[0]))))
