from .. import mapper, Mapper, LegacyItemAccess
from collections import defaultdict
import re

segement_sep = re.compile(" *---.*---.*")
vg_name_line = re.compile(" +VG Name\ +.*")


@mapper('lvdisplay')
class LvDisplay(Mapper, LegacyItemAccess):
    """
    The normal lvdisplay content looks like this:

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


    This mapper returns a dict with volumes and debug keys.
    'Volumne group' and 'Logical volumn' are grouped inside volumes key
    A typical output looks like:
    {
        "debug": [
            "Adding lvsapp01ap01:0 as an user of lvsapp01ap01_mlog"
        ],
        "volumes": {
            "Logical volume": [
                {
                    "LV Name": "lvsapp01ap01-old",
                    "LV Path": "/dev/vgp01app/lvsapp01ap01-old",
                    ...
                    "VG Name": "vgp01app",
                    "debug": [
                        "    global/lvdisplay_shows_full_device_path not found in config: defaulting to 0"
                    ]
                },
                {
                    "LV Name": "lvsapp01ap02",
                    "LV Path": "/dev/vgp01app/lvsapp01ap02",
                    ...
                    "VG Name": "vgp01app",
                    "debug": [
                        "    global/lvdisplay_shows_full_device_path not found in config: defaulting to 0"
                    ]
                }
            ],
            "Volume group": [
                {
                    "VG Name": "vgp01app",
                    "VG Size": "399.98 GiB",
                    ...
                    "VG UUID": "JVgCxE-UY84-C0Gk-8Cmn-UGXu-UHo0-9Qa4Re",
                }
            ]
        }
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
