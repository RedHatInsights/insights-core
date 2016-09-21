from .. import mapper


FILTER_INFO = list()

"""
ERROR_KEY = "LVM_FILTER_ISSUE"
"""
FILTER_INFO.append("Couldn't find device with uuid")
FILTER_INFO.append("physical volumes missing")


@mapper('vgdisplay')
def get_vginfo(context):
    """
    Returns a list of dicts and list contain debug info:
    - the keys in each dict are the row headers
    - each item in the list represents a VG or list contain debug info
    - there is a empty line between different VG
    {
        "vginfo_dict":
      [
        {
            'VG Name': 'rhel_hp-dl160g8-3',
            'Format': 'lvm2',
            'VG Access': 'read/write',
            'Free  PE / Size': '11 / 44.00 MiB',
            'Metadata Sequence No': '5',
            'Alloc PE / Size': '119098 / 465.23 GiB',
            'Total PE': '119109',
            'VG UUID': 'by0Dl3-0lpB-MxEz-f6GO-9LYO-YRAQ-GufNZD',
            'Metadata Areas': '1'
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
    all_dict = {}
    vginfo_dict_list = []
    vginfo_dict = {}
    debug_info = []
    for line in context.content:
        if 'System ID' in line or '--- Volume' in line:
            continue
        if any(debug in line for debug in FILTER_INFO):
            line = line.strip()
            debug_info.append(line)
            continue
        elif line.strip() and not any(debug in line for debug in FILTER_INFO):
            if line.startswith('Metadata Sequence'):
                (key, value) = line.split('  ', 1)
            else:
                (key, value) = line.split('   ', 1)
            vginfo_dict[key.strip()] = value.strip()
        # Empty line indicates the end of a VG
        else:
            # Record the parsed VG
            vginfo_dict_list.append(vginfo_dict)
            vginfo_dict = {}
    # Record the last VG and debug info
    set_info = list(set(debug_info))
    vginfo_dict_list.append(vginfo_dict) if vginfo_dict else None
    all_dict['vginfo_dict'] = vginfo_dict_list
    all_dict['debug_info'] = set_info
    return all_dict
