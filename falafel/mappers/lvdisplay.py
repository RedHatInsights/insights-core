from .. import mapper, Mapper, LegacyItemAccess
from collections import defaultdict
import re

segement_sep = re.compile(" *---.*---.*")
vg_name_line = re.compile(" +VG Name\ +.*")


@mapper('lvdisplay')
class LvDisplay(Mapper, LegacyItemAccess):
    """
    Returns a list of dicts and list contain debug info:
    - the keys in each dict are the row headers
    - each item in the list represents a VG or list contain debug info
    - there is a empty line between different VG
    {
      "logical_volume":
      [
        {
            'VG Name': 'rhel_hp-dl160g8-3',
            'Format': 'lvm2',
            'VG Access': 'read/write',schema[0]
            'Total PE': '119109',
            'VG UUID': 'by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZD',
            'Metadata Areas': '1'
            'debug': 'global/lvdisplay_shows_full_device_path not found in config: defaulting to 0'
        },

        {
            'VG Name': 'rhel_hp-dl260g7-4',
            'Format': 'lvm2',
            'VG Access': 'read/write',
            'Free  PE / Size': '11/ 44.00 MiB',
            'VG UUID': 'by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZN',
            'Alloc PE / Size': '119098 / 465.23 GiB'
        }

      ],

      "debug_info":
      [
            "Couldn't find device with uuid VVLmw8-e2AA-ECfW-wDPl-Vnaa-0wW1-utv7tV.",
            "There are 1 physical volumes missing."
      ]
    }
    """

    def parse_content(self, content):
        self.data = {}
        segment = []
        segment_type = ''
        self.data['debug'] = []
        self.data['volumes'] = defaultdict(list)
        for line in content:
            if segement_sep.match(line):
                self.add_segment(segment_type, segment)
                segment_type = line.split('---')[1].strip()
                segment = []
            else:
                segment.append(line)

        if segment:
            # last segment
            self.add_segment(segment_type, segment)

    def add_segment(self, segment_type, segment):
        if not segment:
            return

        schema = ()
        for line in segment:
            if vg_name_line.match(line):
                indexes = [(m.start(), m.end()) for m in re.finditer("\ +", line)]
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
