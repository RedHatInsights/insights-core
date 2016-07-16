"""
Parse lsblk command output. sometime (dm-) appear in line
Example:
NAME                            MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINT
sda                               8:0    0   80G  0 disk
|-sda1                            8:1    0  256M  0 part  /boot
`-sda2                            8:2    0 79.8G  0 part
  |-volgrp01-root (dm-0)        253:0    0   15G  0 lvm   /
  |-volgrp01-swap (dm-1)        253:1    0    8G  0 lvm   [SWAP]

@:return  a list(dict)
Each dict stand for one line.
"""

from falafel.core.plugins import mapper


@mapper('lsblk')
def get_device_info(context):
    device_list = []
    parent = []
    for line in context.content[1:]:
        device_dict = {}
        if line[0].isalpha():
            cols = line.strip().split()
            parent.append(cols[0])
            device_dict = {"device": cols[0], "type": cols[5], "blanks": 0}
        else:
            if "|  " in line:
                # replace "|  " for using lstrip()
                line = line.replace("|  ", "  ")
            blanks = len(line) - len(line.lstrip())
            previous_blanks = device_list[-1].get('blanks')
            # if (dm-) in line, there will be one more column.
            # if line.split() > column_size, need add addition to get proper column value
            # addition = len(line.split()) - column_size
            addition = 0
            if "(dm-" in line:
                addition = 1
            # determine parent
            if blanks > previous_blanks:
                parent.append(device_list[-1].get('device'))
            elif blanks < previous_blanks:
                for i in range(0, previous_blanks - blanks, 2):
                    # assume the number blanks is multiple of 2
                    parent.pop()
            cols = line.strip().split()
            device_dict["device"] = cols[0].replace('|-', "").replace('`-', "")
            device_dict["type"] = cols[5 + addition]
            device_dict["parent"] = parent[-1]
            device_dict["blanks"] = blanks
            if len(cols) >= (7 + addition):
                device_dict["mountpoint"] = cols[6 + addition]
        device_list.append(device_dict)
    # remove blanks from last dict.
    [line_dict.pop("blanks") for line_dict in device_list]
    return device_list
