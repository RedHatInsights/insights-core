"""
Lvm - Combiner for lvm information
==================================

This shared combiner for LVM parsers consolidates all of the information for
the following information:

* LVS
* PVS
* VGS

The parsers gather this information from multiple locations such as Insights
data and SOS Report data and combines the data. Sample input data and examples
are shown for LVS, with PVS and VGS being similar.

Sample input data for LVS commands as parsed by the parsers::

    # Output of the command:
    # /sbin/lvs -a -o +lv_tags,devices --config="global{locking_type=0}"
    WARNING: Locking disabled. Be careful! This could corrupt your metadata.
    LV   VG   Attr       LSize  Pool Origin Data%  Meta%  Move Log Cpy%Sync Convert LV Tags Devices
    root rhel -wi-ao---- 17.47g                                                             /dev/vda2(512)
    swap rhel -wi-ao----  2.00g                                                             /dev/vda2(0)

    # Output of the command:
    # /sbin/lvs --nameprefixes --noheadings --separator='|' -a -o lv_name,vg_name,lv_size,region_size,mirror_log,lv_attr,devices,region_size --config="global{locking_type=0}"
    WARNING: Locking disabled. Be careful! This could corrupt your metadata.
    LVM2_LV_NAME='root'|LVM2_VG_NAME='rhel'|LVM2_LV_SIZE='17.47g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/vda2(512)'|LVM2_REGION_SIZE='0 '
    LVM2_LV_NAME='swap'|LVM2_VG_NAME='rhel'|LVM2_LV_SIZE='2.00g'|LVM2_REGION_SIZE='0 '|LVM2_MIRROR_LOG=''|LVM2_LV_ATTR='-wi-ao----'|LVM2_DEVICES='/dev/vda2(0)'|LVM2_REGION_SIZE='0 '

Because logical volume names may be duplicated on different volume groups, the
key used for the logical volume information is a named tuple of type `LvVgName`.
Physical volumes and volume groups do not have the same limitation so the
key used for that information is simply the string name of the physical
device or volume group.

Examples:
    >>> lvm_info = shared[Lvm]
    >>> lvm_info.logical_volumes[LvVgName(LV='root', VG='rhel')]
    {
        'Log': '', 'LPerms': None, 'Health': None, 'MaxSync': None, 'Pool_UUID': None, 'DevOpen': None, 'SkipAct': None,
        'Parent': None, 'Descendants': None, 'WhenFull': None, 'Lock_Args': None, 'CacheReadMisses': None, 'Host': None,
        'CacheWriteHits': None, 'Active': None, 'Path': None, 'LV_UUID': None, 'Data': None, 'LV_Tags': None, 'Pool': None,
        'CacheDirtyBlocks': None, 'InitImgSync': None, 'Region': '0', 'LiveTable': None, 'MinSync': None,
        'Devices': '/dev/vda2(512)', 'ActLocal': None, 'Time': None, 'Cpy%Sync': None, 'Modules': None, 'Data_UUID': None, 'Origin': None,
        'Move': None, 'Origin_UUID': None, 'Converting': None, 'LSize': '17.47g', '#Seg': None, 'Ancestors': None, 'Layout': None,
        'Meta%': None, 'Min': None, 'Data%': None, 'AllocLock': None, 'CacheWriteMisses': None, 'AllocPol': None,
        'CacheTotalBlocks': None, 'MergeFailed': None, 'Mismatches': None, 'WBehind': None, 'ActExcl': None, 'ActRemote': None,
        'OSize': None, 'KMin': None, 'LV': 'root', 'InactiveTable': None, 'Move_UUID': None, 'Maj': None, 'Role': None, 'KMaj': None,
        'Convert': None, 'LProfile': None, 'Attr': '-wi-ao----', 'VG': 'rhel', 'KRahead': None, 'Rahead': None, 'Log_UUID': None,
        'MSize': None, 'Merging': None, 'DMPath': None, 'Meta_UUID': None, 'SnapInvalid': None, 'ImgSynced': None,
        'CacheReadHits': None, 'Meta': None, 'Snap%': None, 'Suspended': None, 'FixMin': None, 'CacheUsedBlocks': None, 'SyncAction': None
    }
    >>> lvm_info.logical_volumes[LvVgName('root','rhel')]['LSize']
    '17.47g'
    >>> lvm_info.logical_volume_names
    {LvVgName(LV='root', VG='rhel'), LvVgName(LV='swap', VG='rhel')}
    >>> lvm_info.filter_logical_volumes(lv_filter='root')
    {LvVgName(LV='root', VG='rhel'): {
        'Log': '', 'LPerms': None, 'Health': None, 'MaxSync': None, 'Pool_UUID': None, 'DevOpen': None, 'SkipAct': None,
        'Parent': None, 'Descendants': None, 'WhenFull': None, 'Lock_Args': None, 'CacheReadMisses': None, 'Host': None,
        'CacheWriteHits': None, 'Active': None, 'Path': None, 'LV_UUID': None, 'Data': None, 'LV_Tags': None, 'Pool': None,
        'CacheDirtyBlocks': None, 'InitImgSync': None, 'Region': '0', 'LiveTable': None, 'MinSync': None,
        'Devices': '/dev/vda2(512)', 'ActLocal': None, 'Time': None, 'Cpy%Sync': None, 'Modules': None, 'Data_UUID': None, 'Origin': None,
        'Move': None, 'Origin_UUID': None, 'Converting': None, 'LSize': '17.47g', '#Seg': None, 'Ancestors': None, 'Layout': None,
        'Meta%': None, 'Min': None, 'Data%': None, 'AllocLock': None, 'CacheWriteMisses': None, 'AllocPol': None,
        'CacheTotalBlocks': None, 'MergeFailed': None, 'Mismatches': None, 'WBehind': None, 'ActExcl': None, 'ActRemote': None,
        'OSize': None, 'KMin': None, 'LV': 'root', 'InactiveTable': None, 'Move_UUID': None, 'Maj': None, 'Role': None, 'KMaj': None,
        'Convert': None, 'LProfile': None, 'Attr': '-wi-ao----', 'VG': 'rhel', 'KRahead': None, 'Rahead': None, 'Log_UUID': None,
        'MSize': None, 'Merging': None, 'DMPath': None, 'Meta_UUID': None, 'SnapInvalid': None, 'ImgSynced': None,
        'CacheReadHits': None, 'Meta': None, 'Snap%': None, 'Suspended': None, 'FixMin': None, 'CacheUsedBlocks': None, 'SyncAction': None
    }}
"""

import copy
from collections import namedtuple
from insights.core.plugins import combiner
from insights.parsers.lvm import Lvs, LvsHeadings, Pvs, PvsHeadings, Vgs, VgsHeadings
from insights.parsers.lvm import LvsAll, PvsAll, VgsAll


def get_shared_data(component):
    """
    Returns the actual list of component data based on how data is
    stored in component, either from the `data` attribute or from the
    `data['content']` attribute.

    Returns:
        list: List of component data.
    """
    if component:
        return (copy.deepcopy(component.data)
                if 'content' not in component.data
                else copy.deepcopy(component.data['content']))
    else:
        return []


def to_name_key_dict(data, name_key):
    """
    Iterates a list of dictionaries where each dictionary has a `name_key`
    value that is used to return a single dictionary indexed by those
    values.

    Returns:
        dict: Dictionary keyed by `name_key` values having the information
            contained in the original input list `data`.
    """
    return dict((row[name_key], row) for row in data)


def merge_lvm_data(primary, secondary, name_key):
    """
    Returns a dictionary containing the set of data from primary and secondary
    where values in primary will always be returned if present, and values in
    secondary will only be returned if not present in primary, or if the value
    in primary is `None`.

    Sample input Data::

        primary = [
            {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'name_key': 'xyz'},
            {'a': None, 'b': 12, 'c': 13, 'd': 14, 'name_key': 'qrs'},
            {'a': None, 'b': 12, 'c': 13, 'd': 14, 'name_key': 'def'},
        ]
        secondary = [
            {'a': 31, 'e': 33, 'name_key': 'xyz'},
            {'a': 11, 'e': 23, 'name_key': 'qrs'},
            {'a': 1, 'e': 3, 'name_key': 'ghi'},
        ]

    Returns:
        dict: Dictionary of key value pairs from obj1 and obj2::

            {
                'xyz': {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 33, 'name_key': 'xyz'},
                'qrs': {'a': 11, 'b': 12, 'c': 13, d: 14, e: 23, 'name_key': 'qrs'},
                'def': {'a': None, 'b': 12, 'c': 13, 'd': 14, 'name_key': 'def'},
                'ghi': {'a': 1, 'e': 3, 'name_key': 'ghi'}
            }

    """
    pri_data = to_name_key_dict(primary, name_key)
    # Prime results with secondary data, to be updated with primary data
    combined_data = to_name_key_dict(secondary, name_key)
    for name in pri_data:
        if name not in combined_data:
            # Data only in primary
            combined_data[name] = pri_data[name]
        else:
            # Data in both primary and secondary, pick primary if better or no secondary
            combined_data[name].update(dict(
                (k, v) for k, v in pri_data[name].items()
                if v is not None or k not in combined_data[name]
            ))

    return set_defaults(combined_data)


def set_defaults(lvm_data):
    """dict: Sets all existing null string values to None."""
    for l in lvm_data:
        for k, v in lvm_data[l].items():
            if v == '':
                lvm_data[l][k] = None

    return lvm_data


@combiner([Lvs, LvsHeadings, Pvs, PvsHeadings, Vgs, VgsHeadings])
class Lvm(object):
    """Class implements shared combiner for LVM information."""

    LvVgName = namedtuple('LvVgName', ['LV', 'VG'])
    """Named tuple used as key for logical volumes."""

    def __init__(self, lvs, lvs_headings, pvs, pvs_headings, vgs, vgs_headings):
        # Volume Groups information
        self.volume_groups = merge_lvm_data(get_shared_data(vgs),
                                            get_shared_data(vgs_headings),
                                            'VG')
        """dict: Contains a dictionary of volume group data with keys
            from the original output."""

        # Physical Volumes information
        self.physical_volumes = merge_lvm_data(get_shared_data(pvs),
                                               get_shared_data(pvs_headings),
                                               'PV_KEY')
        """dict: Contains a dictionary of physical volume data with keys
            from the original output."""

        # Logical Volumes information
        # Since logical volume names can be duplicated across volume
        # groups we use a new key that combines the logical volume
        # name with the volume group name to ensure it is unique
        pri_lvs_data = get_shared_data(lvs)
        for l in pri_lvs_data:
            l['LVVG'] = Lvm.LvVgName(LV=l['LV'], VG=l['VG'])
        sec_lvs_data = get_shared_data(lvs_headings)
        for l in sec_lvs_data:
            l['LVVG'] = Lvm.LvVgName(LV=l['LV'], VG=l['VG'])
        self.logical_volumes = merge_lvm_data(pri_lvs_data,
                                              sec_lvs_data,
                                              'LVVG')
        """dict: Contains a dictionary of logical volume data with keys
            from the original output. The key is a tuple of the
            logical volume name and the volume group name. This tuple
            avoids the case where logical volume names are the same
            across volume groups."""

        self.logical_volumes = set_defaults(self.logical_volumes)

        # Since name is not used as the key we need to create the name list
        self.physical_volume_names = set([p['PV'] for p in self.physical_volumes.values()])

    @property
    def volume_group_names(self):
        """set: Returns a set of keys from the volume group information."""
        return set(self.volume_groups.keys())

    @property
    def logical_volume_names(self):
        """set: Returns a set of tuple keys from the logical volume information."""
        return set(self.logical_volumes.keys())

    def filter_volume_groups(self, vg_filter):
        """dict: Returns dictionary of volume group information with keys
            containing `vg_filter`."""
        return dict((k, v) for k, v in self.volume_groups.items() if vg_filter in k)

    def filter_physical_volumes(self, pv_filter):
        """dict: Returns dictionary of physical volume information with keys
            containing `pv_filter`."""
        return dict((k, v) for k, v in self.physical_volumes.items() if pv_filter in k)

    def filter_logical_volumes(self, lv_filter, vg_filter=None):
        """dict: Returns dictionary of logical volume information having the
            `lv_filter` in the logical volume and if specified `vg_filter` in the
            volume group."""
        if vg_filter is None:
            return dict((k, v) for k, v in self.logical_volumes.items()
                        if lv_filter in k.LV)
        else:
            return dict((k, v) for k, v in self.logical_volumes.items()
                        if lv_filter in k.LV and vg_filter in k.VG)


@combiner([LvsAll, PvsAll, VgsAll])
class LvmAll(Lvm):
    """A Lvm like shared combiner for processing LVM information including all rejected
        and accepted devices"""

    def __init__(self, lvsall, pvsall, vgsall):
        # Volume Groups information
        self.volume_groups = merge_lvm_data(get_shared_data(vgsall), [], 'VG')
        """dict: Contains a dictionary of volume group data with keys
            from the original output."""

        # Physical Volumes information
        self.physical_volumes = merge_lvm_data(get_shared_data(pvsall), [], 'PV_KEY')
        """dict: Contains a dictionary of physical volume data with keys
            from the original output."""

        pri_lvs_data = get_shared_data(lvsall)
        for l in pri_lvs_data:
            l['LVVG'] = Lvm.LvVgName(LV=l['LV'], VG=l['VG'])
        self.logical_volumes = merge_lvm_data(pri_lvs_data, [], 'LVVG')
        """dict: Contains a dictionary of logical volume data with keys
            from the original output. The key is a tuple of the
            logical volume name and the volume group name. This tuple
            avoids the case where logical volume names are the same
            across volume groups."""

        self.logical_volumes = set_defaults(self.logical_volumes)

        # Since name is not used as the key we need to create the name list
        self.physical_volume_names = set([p['PV'] for p in self.physical_volumes.values()])
