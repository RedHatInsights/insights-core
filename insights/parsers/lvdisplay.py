"""
LVDisplay - command ``/sbin/lvdisplay``
=======================================

The normal lvdisplay content looks like this::

  Adding lvsapp01ap01:0 as an user of lvsapp01ap01_mlog
  --- Volume group ---
  VG Name               vgp01app
  ...
  VG Size               399.98 GiB
  VG UUID               JVgCxE-UY84-C0Gk-8Cmn-UGXu-UHo0-9Qa4Re
  --- Logical volume ---
  global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/vgp01app/lvsapp01ap01-old
  LV Name                lvsapp01ap01-old
  ...
  VG Name                vgp01app
  --- Logical volume ---
  global/lvdisplay_shows_full_device_path not found in config: defaulting to 0
  LV Path                /dev/vgp01app/lvsapp01ap02
  LV Name                lvsapp01ap02
  ...
  VG Name                vgp01app

The data is compiled into two keys in the ``data`` attribute:

* ``Logical volume``: a list of logical volume dictionaries.
* ``Volume group``: a list of volume group dictionaries.

The keys in each dictionary correspond to the headings found in the
output - for example, the keys in each ``Volume group`` list entry will
include ``VG Name``, ``VG Size``, etc.

In addition, the ``debug`` key in both the ``data`` attribute dictionary
and the ``Logical volume`` and ``Volume group`` dictionaries stores any
debug or warning messages found while parsing the output for that section.

Logical volumes are also available as a dictionary in the ``lvs`` property
and volume groups in the ``vgs`` property, both arranged by name.  Both
contain the same information as the associated list entry in the ``volumes``
dictionary.

Examples:

    >>> lvs = shared(LvDisplay)
    >>> 'volumes' in lvs # direct access via LegacyItemAccess
    True
    >>> 'debug' in lvs.data['volumes'] # access via data property
    True
    >>> for lv in lvs.data['volumes']['Logical volume']:
    ---     print lv['LV Name']
    ---
    lvsapp01ap01-old
    lvsapp01ap02
    >>> lvs.lvs['lvsapp01ap02']['VG Name'] # access to LVs by name
    'vgp01app'
    >>> lvs.vgs['vgp01app']['VG Size'] # access to VGs by name
    '399.98 GiB'

"""

from .. import parser, LegacyItemAccess, CommandParser
from collections import defaultdict
import re
from insights.specs import Specs


@parser(Specs.lvdisplay)
class LvDisplay(CommandParser, LegacyItemAccess):
    """
    Read the output of ``/sbin/lvdisplay``.

    Attributes:
        data(dict): The full data parsed from the output of lvdisplay.
        lvs(dict): A dictionary of logical volumes by name.
        vgs(dict): A dictionary of volume groups by name.
    """

    def parse_content(self, content):
        self.data = {}
        segment = []
        segment_type = ''
        self.data['debug'] = []
        self.data['volumes'] = defaultdict(list)
        for line in content:
            split_line = line.split()
            if segment and len(split_line) >= 2 and split_line[0] == '---' and split_line[-1] == '---':
                self.add_segment(segment_type, segment)
                segment_type = " ".join(split_line[1:len(split_line) - 1])
                segment = []
            else:
                segment.append(line)

        if segment:
            # last segment
            self.add_segment(segment_type, segment)

        self.data['volumes'] = dict(self.data['volumes'])

        # Add lvs and vgs properties with dicts from the data collected
        if 'Volume group' in self.data['volumes']:
            self.vgs = {}
            for vg in self.data['volumes']['Volume group']:
                self.vgs[vg['VG Name']] = vg
        if 'Logical volume' in self.data['volumes']:
            self.lvs = {}
            for lv in self.data['volumes']['Logical volume']:
                self.lvs[lv['LV Name']] = lv

    def add_segment(self, segment_type, segment):
        schema = ()
        for line in segment:
            if line.lstrip().startswith('VG Name'):
                indexes = [(m.start(), m.end()) for m in re.finditer(r"\ +", line)]
                schema = (indexes[0][1], indexes[2][1])
                break

        if not schema:
            self.data['debug'].extend(segment)
        else:
            self.data['volumes'][segment_type].append(self.parse_segment(segment, schema))

    def parse_segment(self, lines, schema):
        segment = {}
        debug = []
        for line in lines:
            name = line[schema[0]:schema[1]]
            if name.startswith(' '):
                debug.append(line[schema[0]:])
            else:
                value = line[schema[1]:].strip()
                name = name.strip()
                if not name and not value:
                    continue
                segment[name] = value

        segment['debug'] = debug
        return segment
