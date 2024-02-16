"""
Logical Volume Management configuration and status
==================================================

Parsers for lvm data based on output of various commands and file contents.

This module contains the classes that parse the output of the commands `lvs`,
`pvs`, and `vgs`, and the content of the files `/etc/lvm/lvm.conf`,
`/etc/lvm/devices/system.devices`.

Pvs - command ``/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all``
------------------------------------------------------------------------------------

PvsHeadings - command ``pvs -a -v -o +pv_mda_free,pv_mda_size,pv_mda_count,pv_mda_used_count,pe_count --config="global{locking_type=0}"``
-----------------------------------------------------------------------------------------------------------------------------------------

Vgs - command ``/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all``
------------------------------------------------------------------------------------

VgsHeadings - command ``vgs -v -o +vg_mda_count,vg_mda_free,vg_mda_size,vg_mda_used_count,vg_tags --config="global{locking_type=0}"``
-------------------------------------------------------------------------------------------------------------------------------------

Lvs - command ``/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype,seg_monitor --config="global{locking_type=0}"``
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

LvsHeadings - command ``/sbin/lvs -a -o +lv_tags,devices --config="global{locking_type=0}"``
--------------------------------------------------------------------------------------------

LvmConf - file ``/etc/lvm/lvm.conf``
------------------------------------

LvmSystemDevices - file ``/etc/lvm/devices/system.devices``
-----------------------------------------------------------

LvmFullReport - command ``/sbin/lvm fullreport -a --reportformat json``
-----------------------------------------------------------------------

"""
from __future__ import print_function

import json

from insights.core import CommandParser, JSONParser, LegacyItemAccess, Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.parsers import get_active_lines, optlist_to_dict, parse_fixed_table
from insights.specs import Specs
from insights.util import deprecated
from insights.util import parse_keypair_lines


def map_keys(pvs, keys):
    """
    Add human readable key names to dictionary while leaving any existing key names.
    """
    rs = []
    for pv in pvs:
        r = dict((v, None) for k, v in keys.items())
        for k, v in pv.items():
            if k in keys:
                r[keys[k]] = v
            r[k] = v
        rs.append(r)
    return rs


def find_warnings(content):
    """Look for lines containing warning/error/info strings instead of data."""
    keywords = [
        k.lower()
        for k in [
            "WARNING",
            "Couldn't find device",
            "Configuration setting",
            "read failed",
            "Was device resized?",
            "Invalid argument",
            "leaked on lvs",
            "Checksum error",
            "is exported",
            "failed.",
            "Invalid metadata",
            "response failed",
            "duplicate",
            "not found",
            "Missing device",
            "Internal error",
            "Input/output error",
            "Incorrect metadata",
            "Cannot process volume",
            "No such file or directory",
            "Logging initialised",
            "changed sizes",
            "vsnprintf failed",
            "write failed",
            "correction failed",
            "Failed to write",
            "Couldn't read",
            "marked missing",
            "Attempt to close device",
            "Ignoring supplied major",
            "not match metadata",
            "Reading VG",
            "Error reading device"
        ]
    ]
    for l in content:
        lower = l.strip().lower()
        # Avoid hitting keywords inside the data
        if not lower.startswith("lvm2"):
            if any(k in lower for k in keywords):
                yield l


class LvmHeadings(CommandParser):
    """Base class for parsing LVM data in table format."""

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        return self.data[item]


class Lvm(CommandParser):
    """Base class for parsing LVM data in key=value format."""

    def parse_content(self, content):
        if "Unrecognised field:" in content[-1]:
            raise ParseException(content[-1])
        d = {"warnings": set(find_warnings(content))}
        content = [l for l in content
                   if l not in d["warnings"] and not l.startswith("File descriptor ")]
        d["content"] = list(map_keys(parse_keypair_lines(content), self.KEYS))
        self.data = d if d else None

    def __iter__(self):
        return iter(self.data["content"])

    def __len__(self):
        return len(self.data["content"])

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data["content"][key]
        for i in self.data["content"]:
            if i[self.PRIMARY_KEY] == key:
                return i
        return None

    @property
    def locking_disabled(self):
        """bool: Returns True if any lines in input data indicate locking is disabled."""
        return any(l for l in self.data["warnings"] if "Locking disabled" in l)

    @property
    def warnings(self):
        """list: Returns a list of lines from input data containing
            warning/error/info strings.
        """
        return self.data["warnings"]


@parser(Specs.pvs_noheadings)
class Pvs(Lvm):
    """
    Parse the output of the `/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all` command.

    Parse each line in the output of pvs based on the of pvs datasource in
    `insights/specs/` Output sample of pvs::

        LVM2_PV_FMT=''|LVM2_PV_UUID=''|LVM2_DEV_SIZE='500.00m'|...
        LVM2_PV_FMT='lvm2'|LVM2_PV_UUID='JvSULk-ileq-JbuS-GGgg-jkif-thuW-zvFBEl'|LVM2_DEV_SIZE='476.45g'|...

    Returns a list like::

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

    Since it is possible to have two PV's with the same name (for example *unknown device*) a
    unique key for each PV is created by joining the `PV_NAME and PV_UUID fields with a `+`
    character.  This key is added to the dictionary as the `PV_KEY` field.
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
        "LVM2_PV_MISSING": "Missing",
    }

    PRIMARY_KEY = "PV"

    def parse_content(self, content):
        super(Pvs, self).parse_content(content)
        for pv in self.data["content"]:
            pv_name = pv.get("PV") if pv.get("PV") is not None else "no_name"
            pv_uuid = pv.get("PV_UUID") if pv.get("PV_UUID") is not None else "no_uuid"
            pv.update({"PV_KEY": "+".join([pv_name, pv_uuid])})

    def vg(self, name):
        """Return all physical volumes assigned to the given volume group"""
        return [i for i in self.data["content"] if i["VG"] == name]


@parser(Specs.pvs_noheadings_all)
class PvsAll(Pvs):
    """
    Parse the output of the `/sbin/pvs --nameprefixes --noheadings --separator='|' -a -o pv_all,vg_name --config='global{locking_type=0} devices{filter=["a|.*|"]}'` command.

    Uses the ``Pvs`` class defined in this module.
    """

    pass


@parser(Specs.pvs_headings)
class PvsHeadings(LvmHeadings):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.lvm.Pvs` instead.

    Parses the output of the
    `pvs -a -v -o +pv_mda_free,pv_mda_size,pv_mda_count,pv_mda_used_count,pe_count --config="global{locking_type=0}"`
    command.

    Since it is possible to have two PV's with the same name (for example *unknown device*) a
    unique key for each PV is created by joining the `PV_NAME and PV_UUID fields with a `+`
    character.  This key is added to the resulting dictionary as the `PV_KEY` field.

    Sample input::

          WARNING: Locking disabled. Be careful! This could corrupt your metadata.
            Scanning all devices to update lvmetad.
            No PV label found on /dev/loop0.
            No PV label found on /dev/loop1.
            No PV label found on /dev/sda1.
            No PV label found on /dev/fedora/root.
            No PV label found on /dev/sda2.
            No PV label found on /dev/fedora/swap.
            No PV label found on /dev/fedora/home.
            No PV label found on /dev/mapper/docker-253:1-2361272-pool.
            Wiping internal VG cache
            Wiping cache of LVM-capable devices
          PV                                                    VG     Fmt  Attr PSize   PFree DevSize PV UUID                                PMdaFree  PMdaSize  #PMda #PMdaUse PE
          /dev/fedora/home                                                  ---       0     0  418.75g                                               0         0      0        0      0
          /dev/fedora/root                                                  ---       0     0   50.00g                                               0         0      0        0      0
          /dev/fedora/swap                                                  ---       0     0    7.69g                                               0         0      0        0      0
          /dev/loop0                                                        ---       0     0  100.00g                                               0         0      0        0      0
          /dev/loop1                                                        ---       0     0    2.00g                                               0         0      0        0      0
          /dev/mapper/docker-253:1-2361272-pool                             ---       0     0  100.00g                                               0         0      0        0      0
          /dev/mapper/luks-7430952e-7101-4716-9b46-786ce4684f8d fedora lvm2 a--  476.45g 4.00m 476.45g FPLCRf-d918-LVL7-6e3d-n3ED-aiZv-EesuzY        0   1020.00k     1        1 121970
          /dev/sda1                                                         ---       0     0  500.00m                                               0         0      0        0      0
          /dev/sda2                                                         ---       0     0  476.45g                                               0         0      0        0      0
            Reloading config files
            Wiping internal VG cache

    Attributes:
        data (list): List of dicts, each dict containing one row of the table
            with column headings as keys.
        warnings (set): Set of lines from input data containing
            warning strings.

    Examples:
        >>> pvs_data[0]['PV']
        '/dev/fedora/home'
        >>> pvs_data[0]['PMdaSize']
        '0'

    """
    def __init__(self, *args, **kwargs):
        deprecated(
            PvsHeadings,
            "Please use insights.parsers.lvm.Pvs instead.",
            "3.6.0"
        )
        super(PvsHeadings, self).__init__(*args, **kwargs)

    PRIMARY_KEY = Pvs.PRIMARY_KEY

    def parse_content(self, content):
        self.warnings = set(find_warnings(content))
        content = [l for l in content if l not in self.warnings]
        self.data = parse_fixed_table(
            content,
            heading_ignore=["PV "],
            header_substitute=[("PV UUID", "PV_UUID"), ("1st PE", "1st_PE")],
            trailing_ignore=["Reloading", "Wiping"],
        )
        self.data = map_keys(self.data, Pvs.KEYS)
        for pv in self.data:
            pv_name = pv.get("PV") if pv.get("PV") is not None else "no_name"
            pv_uuid = pv.get("PV_UUID") if pv.get("PV_UUID") is not None else "no_uuid"
            pv.update({"PV_KEY": "+".join([pv_name, pv_uuid])})

    def vg(self, name):
        """Return all physical volumes assigned to the given volume group"""
        return [i for i in self.data if i["VG"] == name]


@parser(Specs.vgs_noheadings)
class Vgs(Lvm):
    """
    Parse the output of the `/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all` command.

    Parse each line in the output of vgs based on the vgs datasource in
    `insights/specs/` Output sample of vgs::

        LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='YCpusB-LEly-THGL-YXhC-t3q6-mUQV-wyFZrx'|LVM2_VG_NAME='rhel'|LVM2_VG_ATTR='wz--n-'|...
        LVM2_VG_FMT='lvm2'|LVM2_VG_UUID='123456-LEly-THGL-YXhC-t3q6-mUQV-123456'|LVM2_VG_NAME='fedora'|LVM2_VG_ATTR='wz--n-'|...

    Returns a list like::

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
        "LVM2_VG_LOCK_TYPE": "Lock_Type",
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
        "LVM2_VG_LOCK_ARGS": "Lock Args",
        "LVM2_MAX_LV": "MaxLV",
        "LVM2_VG_SIZE": "VSize",
    }

    PRIMARY_KEY = "VG"


@parser(Specs.vgs_noheadings_all)
class VgsAll(Vgs):
    """
    Parse the output of the `/sbin/vgs --nameprefixes --noheadings --separator='|' -a -o vg_all --config='global{locking_type=0} devices{filter=[\"a|.*|\"]}'` command.

    Uses the ``Vgs`` class defined in this module.
    """

    pass


@parser(Specs.vgs_headings)
class VgsHeadings(LvmHeadings):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.lvm.Vgs` instead.

    Parses output of the
    `vgs -v -o +vg_mda_count,vg_mda_free,vg_mda_size,vg_mda_used_count,vg_tags --config="global{locking_type=0}"` command.

    Sample input::

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

    Attributes:
        data (list): List of dicts, each dict containing one row of the table
            with column headings as keys.
        warnings (set): Set of lines from input data containing
            warning strings.

    Examples:
        >>> vgs_info.data[0]['VG']
        'DATA_OTM_VG'
        >>> vgs_info.data[0]['VG_UUID']
        'xK6HXk-xl2O-cqW5-2izb-LI9M-4fV0-dAzfcc'
    """
    def __init__(self, *args, **kwargs):
        deprecated(
            VgsHeadings,
            "Please use insights.parsers.lvm.Vgs instead.",
            "3.6.0"
        )
        super(VgsHeadings, self).__init__(*args, **kwargs)

    PRIMARY_KEY = Vgs.PRIMARY_KEY

    def parse_content(self, content):
        self.warnings = set(find_warnings(content))
        content = [l for l in content if l not in self.warnings]
        self.data = parse_fixed_table(
            content,
            heading_ignore=["VG "],
            header_substitute=[("VG Tags", "VG_Tags"), ("VG UUID", "VG_UUID")],
            trailing_ignore=["Reloading", "Wiping"],
        )
        self.data = map_keys(self.data, Vgs.KEYS)


@parser(Specs.lvs_noheadings)
class Lvs(Lvm):
    """
    Parse the output of the `/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent,segtype,seg_monitor --config="global{locking_type=0}"` command.

    Parse each line in the output of lvs based on the lvs datasource in
    `insights/specs/`:

    Output sample of lvs::

        LVM2_LV_UUID='KX68JI-8ISN-YedH-ZYDf-yZbK-zkqE-3aVo6m'|LVM2_LV_NAME='docker-poolmeta'|LVM2_LV_FULL_NAME='rhel/docker-poolmeta'|...
        LVM2_LV_UUID='123456-8ISN-YedH-ZYDf-yZbK-zkqE-123456'|LVM2_LV_NAME='rhel_root'|LVM2_LV_FULL_NAME='rhel/rhel_root'|LVM2_LV_PATH='/dev/rhel/docker-poolmeta'|...

    Return a list, as shown below::

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
        "LVM2_CONVERT_LV_UUID": "Convert_UUID",
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
        "LVM2_REGION_SIZE": "Region",
        "LVM2_SEGTYPE": "SegType",
        "LVM2_SEG_MONITOR": "Monitor",
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


@parser(Specs.lvs_noheadings_all)
class LvsAll(Lvs):
    """
    Parse the output of the `/sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,lv_size,lv_attr,mirror_log,vg_name,devices,region_size,data_percent,metadata_percent --config='global{locking_type=0} devices{filter=["a|.*|"]}'` command.

    Uses the ``Lvs`` class defined in this module.
    """

    pass


@parser(Specs.lvs_headings)
class LvsHeadings(LvmHeadings):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.lvm.Lvs` instead.

    Process output of the command `/sbin/lvs -a -o +lv_tags,devices --config="global{locking_type=0}"`.

    Sample Input data::

        WARNING: Locking disabled. Be careful! This could corrupt your metadata.
        LV          VG      Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert LV Tags Devices
        lv_app      vg_root -wi-ao---- 71.63g                                                             /dev/sda2(7136)
        lv_home     vg_root -wi-ao----  2.00g                                                             /dev/sda2(2272)
        lv_opt      vg_root -wi-ao----  5.00g                                                             /dev/sda2(2784)
        lv_root     vg_root -wi-ao----  5.00g                                                             /dev/sda2(0)
        lv_tmp      vg_root -wi-ao----  1.00g                                                             /dev/sda2(4064)
        lv_usr      vg_root -wi-ao----  5.00g                                                             /dev/sda2(4320)
        lv_usrlocal vg_root -wi-ao----  1.00g                                                             /dev/sda2(5600)
        lv_var      vg_root -wi-ao----  5.00g                                                             /dev/sda2(5856)
        swap        vg_root -wi-ao----  3.88g                                                             /dev/sda2(1280)

    Attributes:
        data (list): List of dicts, each dict containing one row of the table
            with column headings as keys.
        warnings (set): Set of lines from input data containing
            warning strings.

    Examples:
        >>> lvs_info.data[0]['Devices']
        '/dev/sda2(7136)'
        >>> lvs_info.data[1]['LSize']
        '2.00g'
    """
    def __init__(self, *args, **kwargs):
        deprecated(
            LvsHeadings,
            "Please use insights.parsers.lvm.Lvs instead.",
            "3.6.0"
        )
        super(LvsHeadings, self).__init__(*args, **kwargs)

    PRIMARY_KEY = Lvs.PRIMARY_KEY

    def parse_content(self, content):
        self.warnings = set(find_warnings(content))
        content = [l for l in content if l not in self.warnings]
        self.data = parse_fixed_table(
            content, heading_ignore=["LV "], header_substitute=[("LV Tags", "LV_Tags")]
        )
        self.data = map_keys(self.data, Lvs.KEYS)


KEYS_WITH_SPACES = []
for cls in (Lvs, Pvs, Vgs):
    KEYS_WITH_SPACES.extend([k for k in cls.KEYS.values() if " " in k])


LVM_CONF_FILTERS = [
    "locking_type",  # CMIRROR_PERF_ISSUE
    "filter",  # LVM_CONF_REMOVE_BOOTDEV HA_LVM_RELOCATE_ISSUE LVM_FILTER_ISSUE
    "volume_list",  # HA_LVM_RELOCATE_ISSUE
]
add_filter(Specs.lvm_conf, LVM_CONF_FILTERS)


@parser(Specs.lvm_conf)
class LvmConf(LegacyItemAccess, Parser):
    """
    Parses contents of the `/etc/lvm/lvm.conf` file.

    Sample Input::

        locking_type = 1
        #locking_type = 2
        # volume_list = [ "vg1", "vg2/lvol1", "@tag1", "@*" ]
        volume_list = [ "vg2", "vg3/lvol3", "@tag2", "@*" ]
        # filter = [ "a|loop|", "r|/dev/hdc|", "a|/dev/ide|", "r|.*|" ]

        filter = [ "r/sda[0-9]*$/",  "a/sd.*/" ]
        filter = [ "a/sda[0-9]*$/",  "r/sd.*/" ]
        shell {
            history_size = 100
        }

    Examples:
        >>> 'vg2' in lvm_conf_data.data.get('volume_list')
        True
        >>> lvm_conf_data.get("locking_type")
        1
    """

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
                (key, value) = [item.strip() for item in line.split("=", 1)]
                try:
                    lvm_conf_dict[key] = json.loads(value)
                except Exception:
                    lvm_conf_dict[key] = value
        self.data = lvm_conf_dict


@parser(Specs.lvmconfig)
class LvmConfig(CommandParser):
    def parse_content(self, content):
        self.data = dict()
        key = None
        for line in content:
            line = line.rstrip()
            if not line:
                continue

            if line[-1] == "{":
                key = line.split()[0]
            elif line[0] == "}":
                key = None
            elif line[0] == "\t":
                k, v = line.strip().split("=", 1)
                # umask=077 will raise exception, and also no need to
                # transfer it, just keep it as string
                if k != 'umask':
                    try:
                        v = json.loads(v)
                    except Exception:
                        raise ParseException("Failed to parse line %s." % line)
                self.data.setdefault(key, {}).update({k: v})
            else:
                pass  # inferring this a stderr, so skipping


@parser(Specs.lvm_system_devices)
class LvmSystemDevices(Parser, dict):
    """
    Parse the content of the ``/etc/lvm/devices/system.devices`` file.
    It returns a dict. The key is the device id, the value is a dict of
    other info.

    Sample input::

        VERSION=1.1.2
        IDTYPE=devname IDNAME=/dev/vda2 DEVNAME=/dev/vda2 PVID=phl0clFbAokp9UXqbIgI5YYQxuTIJVkD PART=2

    Sample output::

        {
            '/dev/vda2': {
                'IDTYPE': 'devname',
                'DEVNAME': '/dev/vda2',
                'PVID': 'phl0clFbAokp9UXqbIgI5YYQxuTIJVkD',
                'PART': '2'
            }
        }

    Example:
        >>> type(devices)
        <class 'insights.parsers.lvm.LvmSystemDevices'>
        >>> devices['/dev/vda2']['IDTYPE']
        'devname'
        >>> devices['/dev/vda2']['PVID']
        'phl0clFbAokp9UXqbIgI5YYQxuTIJVkD'

    Raises:
        SkipComponent: when there is no device info.
    """

    def parse_content(self, content):
        for line in content:
            if 'IDNAME' in line:
                dict_info = optlist_to_dict(line, opt_sep=None)
                self[dict_info.pop('IDNAME')] = dict_info
        if not self:
            raise SkipComponent("No valid content.")


@parser(Specs.lvm_fullreport)
class LvmFullReport(JSONParser):
    """
    Parse the output of the command ``/usr/sbin/lvm fullreport -a --reportformat json``.
    Output is in JSON format so the JSONParser will be used.

    Sample input (actual input is in JSON format, data has been changed here to show the relationship
    between volume groups, physical valumes and logical volumes)::

        {
            "report": [
                {
                    "vg": [ { vg_name:vg1, vg_uuid:111, properties of vg1 } ],
                    "pv": [ { pv_name:/dev/foo, pv_uuid:222, properties of foo },
                            { pv_name:/dev/bar, pv_uuid:333, properties of bar },
                            more pvs ],
                    "lv": [ { lv_name:lv1, lv_uuid:444, properties of lv1 },
                            { lv_name:lv2, lv_uuid:555, properties of lv2 },
                            more lvs ],
                    "pvseg": [ { ..., pv_uuid:222, ... },
                               { ..., pv_uuid:222, ... },
                               { ..., pv_uuid:333, ... },
                               more pvsegs ],
                    "seg": [ { ..., lv_uuid:444, ... },
                             { ..., lv_uuid:555, ... },
                             { ..., lv_uuid:555, ... },
                             more segs ]
                },
                {
                    "vg": [ { vg_name:rhel, vg_uuid:112, properties of rhel } ],
                    "pv": [ { pv_name:/dev/foo2, pv_uuid:223, properties of foo2 },
                            { pv_name:/dev/bar2, pv_uuid:334, properties of bar2 },
                            more pvs ],
                    "lv": [ { lv_name:lv12, lv_uuid:442, properties of lv12 },
                            { lv_name:lv22, lv_uuid:5552, properties of lv22 },
                            more lvs ],
                    "pvseg": [ { ..., pv_uuid:223, ... },
                               { ..., pv_uuid:223, ... },
                               { ..., pv_uuid:334, ... },
                               more pvsegs ],
                    "seg": [ { ..., lv_uuid:442, ... },
                             { ..., lv_uuid:5552, ... },
                             { ..., lv_uuid:5552, ... },
                             more segs ]
                },
                # Orphan volume group (pv's not associated with a vg)
                {
                    "pv": [ {...} ],
                    "pvseg": [ {...} ]
                }
            ]
        }

    Output will be a python object in the same structure as the JSON::

        {
            "report": [
                {
                  "vg": [ {"vg_name": "vg1", ...}, ... ],
                  "pv": [ {"pv_name": "/dev/sdg", ...), ... ],
                  "lv": [ {"lv_name": "[fast1_cvol]", ...}, ... ],
                  "pvseg": [ {"pvseg_start": "0", ...}, ... ],
                  "seg": [ {"segtype": "cache-pool", ...}, ... ]
                },
                {
                  "vg": [ {"vg_name": "rhel", ...}, ... ],
                  "pv": [ {"pv_name": "/dev/sdd", ...), ... ],
                  "lv": [ {"lv_name": "[lvm_lock]", ...}, ... ],
                  "pvseg": [ {"pvseg_start": "0", ...}, ... ],
                  "seg": [ {"segtype": "linear", ...}, ... ]
                },
                ...
                {
                  "pv": [ {...} ],
                  "pvseg": [ {...} ]
                }
            ]
        }

    Attributes:
        warnings(list): List of warning lines included at the beginning of input
        volume_groups(dict): Dictionary with vg_name as the key, contains a dictionary including
            all information for the volume group. The vg element is represented as a list but
            will only have a single item which is that volumn group::

                {
                    "vg1": {
                        "vg": [ {"vg_name": "global", ...}, ... ],
                        "pv": [ {"pv_name": "/dev/sdd", ...), ... ],
                        "lv": [ {"lv_name": "[lvm_lock]", ...}, ... ],
                        "pvseg": [ {"pvseg_start": "0", ...}, ... ],
                        "seg": [ {"segtype": "linear", ...}, ... ]
                    },
                    ...
                }

        orphan_volume_group(dict): Dictionary of pv's and pvseg's not associated with a volume group::

            {
                "pv": [ {"pv_name": "/dev/sda", ...), ... ],
                "pvseg": [ {"pvseg_start": "0", ...}, ... ],
            }

    Example:
        >>> type(lvm_fullreport)
        <class 'insights.parsers.lvm.LvmFullReport'>
        >>> len(lvm_fullreport.volume_groups)
        2
        >>> sorted(lvm_fullreport.volume_groups.keys()) == ['rhel', 'vg1']
        True
        >>> lvm_fullreport.volume_groups['vg1']['pv'][0]['pv_name'] == '/dev/vdb'
        True

    Raises:
        SkipComponent: when there is no device info.
    """
    def parse_content(self, content):
        self.warnings = []
        skip_to_line = len(content)
        for ndx, line in enumerate(content):
            if line.strip().startswith('{'):
                skip_to_line = ndx
                break
            self.warnings.append(line)

        if skip_to_line >= len(content):
            raise SkipComponent("No LVM information in fullreport")

        super(LvmFullReport, self).parse_content(content[skip_to_line:])

        if not self.data['report']:
            raise SkipComponent("No LVM information in fullreport")

        vgs = self.data['report']
        self.volume_groups = dict()
        self.orphan_volume_group = dict()
        for vg_data in vgs:
            if 'vg' in vg_data:
                self.volume_groups[vg_data['vg'][0]['vg_name']] = vg_data
            else:
                self.orphan_volume_group = vg_data


if __name__ == "__main__":
    # This is a quick script to generate the key mappings in each subclass.
    # Run each lvm command with --separator="|", --nameprefixes and *not* --noheadings

    import sys
    from collections import OrderedDict

    content = sys.stdin.read().splitlines()
    headers = [h.strip().replace(" ", "_") for h in content[0].split("|")]
    nameprefixes = [
        v.split("=")[0].strip() for v in content[1].replace("0 ", "0").split("|")
    ]
    pairs = zip(nameprefixes, headers)
    print(json.dumps(OrderedDict(sorted(pairs))))
