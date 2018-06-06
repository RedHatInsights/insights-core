"""
VgDisplay - command ``vgdisplay``
=================================

"""

from .. import parser, CommandParser

import re
from insights.specs import Specs


@parser(Specs.vgdisplay)
class VgDisplay(CommandParser):
    """
    Parse the output of the ``vgdisplay -vv`` or ``vgdisplay`` commands.

    The ``vg_list`` property is the main access to the list of volume groups
    in the command output.  Each volume group is stored as a dictionary of
    keys and values drawn from the property list of the volume group.  The
    volume group's logical and physical volumes are stored in the 'Logical
    Volumes' and 'Physical Volumes' sub-keys, respectively.

    Sample command output of ``vgdisplay -vv`` (pruned for clarity)::

        Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV.

        --- Volume group ---
        VG Name               RHEL7CSB
        System ID
        Format                lvm2
        Metadata Areas        1
        Metadata Sequence No  13
        ...

        --- Logical volume ---
        LV Path                /dev/RHEL7CSB/Root
        LV Name                Root
        VG Name                RHEL7CSB
        LV Size                29.30 GiB
        ...

        --- Physical volumes ---
        PV Name               /dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194
        PV UUID               EfWV9V-03CX-E6zc-JkMw-yQae-wdzp-Je1KUn
        PV Status             allocatable
        Total PE / Free PE    118466 / 4036

    Volume groups are kept in the ``vg_list`` property in the order they were
    found in the file.

    Lines containing 'Couldn't find device with uuid' and 'missing physical
    volume' are stored in a ``debug_info`` property.

    Examples:
        >>> vg_info = shared[VgDisplay]
        >>> len(vg_info.vg_list)
        1
        >>> vgdata = vg_info.vg_list[0]
        >>> vgdata['VG Name']
        'RHEL7CSB'
        >>> vgdata['VG Size']
        '462.76 GiB'
        >>> 'Logical Volumes' in vgdata
        True
        >>> lvs = vgdata['Logical Volumes']
        >>> type(lvs)
        dict
        >>> lvs.keys()  # Note - keyed by device name
        ['/dev/RHEL7CSB/Root']
        >>> lvs['/dev/RHEL7CSB/Root']['LV Name']
        'Root'
        >>> lvs['/dev/RHEL7CSB/Root']['LV Size']
        '29.30 GiB'
        >>> 'Physical Volumes' in vgdata
        True
        >>> vgdata['Physical Volumes'].keys()
        ['/dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194']
        >>> vgdata['Physical Volumes']['/dev/mapper/luks-96c66446-77fd-4431-9508-f6912bd84194']['PV UUID']
        'EfWV9V-03CX-E6zc-JkMw-yQae-wdzp-Je1KUn'
        >>> vg_info.debug_info
        ["Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV."]
    """

    _FILTER_INFO = [
        "Couldn't find device with uuid",
        "physical volumes missing",
    ]

    def parse_content(self, content):
        self.vg_list = []
        self.debug_info = []

        # Each section starts with a '(VG|LV|PV) Name' header.  This then
        # sets the amount of space between the start of the key and the start
        # of the value.  Unfortunately, there may be only one space between
        # the key and the value and there are spaces in the key, so it's
        # impossible to tell where the key stops and the value ends on space
        # alone.  However, the header sets the left-most column the value
        # starts at, so once we pick up the header we ignore the regex match
        # and get the key and value as substrings.
        header_re = re.compile(r'^(?P<key>VG Name|LV Path|PV Name)\s+(?P<val>\S.*)$')
        # To save different handling, we use this to refer to the current
        # dictionary we're storing data in, whether it be a VG, LV or PV.
        current_data_store = None
        value_start_column = 0
        # Each section of key-value data starts with the header as above and
        # ends with a blank line.  This prevents parsing of random error
        # and information messages as key-value pairs.
        in_keyval_section = False
        for line in content:
            line = line.strip()
            if any(debug in line for debug in self._FILTER_INFO):
                if line not in self.debug_info:
                    self.debug_info.append(line)
                in_keyval_section = False

            match = header_re.match(line)
            # Headers mark the start of a keyval section, but they do match
            # inside, so only match if outside a keyval section.
            if not in_keyval_section and match:
                in_keyval_section = True
                key, value = match.group('key', 'val')
                # Determine column for start of value - remember, this string
                # is now stripped so this may look different from your examples
                value_start_column = line.index(value)
                if key == "VG Name":
                    # New Volume Group - new vg_info_dict entry
                    self.vg_list.append({
                        # Logical and Physical volumes stored by name / device
                        'Logical Volumes': {},
                        'Physical Volumes': {},
                        'VG Name': value,
                    })
                    current_data_store = self.vg_list[-1]
                elif key == 'LV Path':
                    # New Logical Volume - append to 'Logical Volumes'
                    current_data_store = {
                        key: value,
                    }
                    self.vg_list[-1]['Logical Volumes'][value] = current_data_store
                else:  # elif key == 'PV Name':
                    # New Physical Volume - append to 'Physical Volumes'
                    current_data_store = {
                        key: value,
                    }
                    self.vg_list[-1]['Physical Volumes'][value] = current_data_store
            elif line == '':
                # Blank line = new section, stop expecting keys and values
                in_keyval_section = False
            elif in_keyval_section and len(line) > value_start_column:
                # Extract key and value by substring
                key = line[:value_start_column].strip()
                value = line[value_start_column:].strip()
                # Finally, add this key/val pair to the current data store.
                current_data_store[key] = value
