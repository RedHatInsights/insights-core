"""
get_multipath_v4_ll - Command output
====================================

This function converts the output of ``multipath -v4 -ll`` into a series of
data structures.  Examples of input data and resultant structure are given in
the help for the function.

Example:
    >>> mpaths = shared[get_multipath_v4_ll]
    >>> length(mpaths)
    2
    >>> mpath[0]['alias']
    'mpathg'
    >>> mpath[0]['size']
    '54T'
    >>> groups = mpath[0]['path_group']
    >>> groups[0]['status']
    'active'
    >>> length(groups[0]['path'])
    4
    >>> path0 = groups[0]['path'][0]
    >>> path0[1]
    'sdc'
    >>> path0[-1]
    'running'
"""

import re
import shlex
from .. import mapper

MPATH_WWID_REG = re.compile(r'\(?([A-Za-z0-9_\s]+)\)?\s+dm-')
PROPERTY_SQBRKT_REG = re.compile(r"\[(?P<key>\w+)=(?P<value>[^\]]+)\]")
PATHGROUP_POLICY_STR = \
    r"(?:policy=')?(?P<policy>(?:round-robin|queue-length|service-time) \d)" + \
    r"(?:' | \[)prio=(?P<priority>\d+)(?:\]\[| status=)" + \
    r"(?P<status>\w+)(?:\]|)"
PATHGROUP_POLICY_REG = re.compile(PATHGROUP_POLICY_STR)
HCTL_REG = re.compile(r'(?:[`|]-(?:\+-)?|\\_) (\d+:){3}\d+')


@mapper('multipath_-v4_-ll')
def get_multipath_v4_ll(context):
    """
    ``multipath_-v4_ll`` command output

    Example input::

        ===== paths list =====
        uuid hcil    dev dev_t pri dm_st chk_st vend/prod/rev       dev_st
             0:0:0:0 sda 8:0   -1  undef ready  VMware,Virtual disk running
             3:0:0:1 sdb 8:16  -1  undef ready  IET,VIRTUAL-DISK    running
             4:0:0:1 sdc 8:32  -1  undef ready  IET,VIRTUAL-DISK    running
        Oct 28 14:02:44 | *word = 0, len = 1
        Oct 28 14:02:44 | *word = E, len = 1
        Oct 28 14:02:44 | *word = 1, len = 1
        Oct 28 14:02:44 | *word = 0, len = 1
        Oct 28 14:02:44 | *word = A, len = 1
        Oct 28 14:02:44 | *word = 0, len = 1
        mpathg (36f01faf000da360b0000033c528fea6d) dm-2 DELL,MD36xxi
        size=54T features='3 queue_if_no_path pg_init_retries 50' hwhandler='1 rdac' wp=rw
        |-+- policy='round-robin 0' prio=0 status=active
        | |- 12:0:0:1 sdc 8:32   active ready running
        | |- 11:0:0:1 sdi 8:128  active ready running
        | |- 15:0:0:1 sdo 8:224  active ready running
        | `- 17:0:0:1 sdv 65:80  active ready running
        `-+- policy='round-robin 0' prio=0 status=enabled
          |- 13:0:0:1 sdf 8:80   active ready running
          |- 14:0:0:1 sdl 8:176  active ready running
          |- 16:0:0:1 sdr 65:16  active ready running
          `- 18:0:0:1 sdx 65:112 active ready running
        mpathe (36f01faf000da3761000004323aa6fbce) dm-4 DELL,MD36xxi
        size=54T features='3 queue_if_no_path pg_init_retries 55' hwhandler='1 rdac' wp=rw
        |-+- policy='round-robin 0' prio=0 status=active
        | |- 13:0:0:2 sdg 8:96   active faulty running
        | |- 14:0:0:2 sdm 8:192  active faulty running
        | |- 16:0:0:2 sds 65:32  active faulty running
        | `- 18:0:0:2 sdy 65:128 active faulty running
        `-+- policy='round-robin 0' prio=0 status=enabled
          |- 12:0:0:2 sdd 8:48   active faulty running
          |- 11:0:0:2 sdj 8:144  active faulty running
          |- 15:0:0:2 sdp 8:240  active faulty running
          `- 17:0:0:2 sdw 65:96  active faulty running
        36001405b1629f80d52a4c898f8856e43 dm-5 LIO-ORG ,block0_sdb
        size=2.0G features='0' hwhandler='0' wp=rw
        |-+- policy='service-time 0' prio=1 status=active
        | `- 3:0:0:0 sdc 8:32 active ready running
        `-+- policy='service-time 0' prio=1 status=enabled
          `- 4:0:0:0 sdb 8:16 active ready running

    Example data structure produced::

        [
         {
            "alias": "mpathg",
            "wwid": "36f01faf000da360b0000033c528fea6d",
            "dm_name": "dm-2",
            "venprod": "DELL,MD36xxi",
            "size": "54T",
            "features": "3 queue_if_no_path pg_init_retries 50",
            "hwhandler": "1 rdac",
            "wp": "rw",
            "path_group": [
                 {
                    "policy": "round-robin 0",
                    "prio": "0"
                    "status": "active"
                    "path": [
                        ['12:0:0:1', 'sdc', '8:32', 'active', 'ready', 'running'],
                        ['11:0:0:1', 'sdi', '8:128', 'active', 'ready', 'running'],
                        ['15:0:0:1', 'sdo', '8:224', 'active', 'ready', 'running'],
                        ['17:0:0:1', 'sdv', '65:80', 'active', 'ready', 'running']
                    ]
                 },
                 {
                    "policy": "round-robin 0",
                    "prio": "0"
                    "status": "enabled"
                    "path": [
                        ['13:0:0:1', 'sdf', '8:80', 'active', 'ready', 'running'],
                        ['14:0:0:1', 'sdl', '8:176', 'active', 'ready', 'running'],
                        ['16:0:0:1', 'sdr', '65:16', 'active', 'ready', 'running'],
                        ['18:0:0:1', 'sdx', '65:112','active', 'ready', 'running']
                    ]
                }
            ]
          },

         {
            "alias": "mpathe",
            "wwid": "36f01faf000da3761000004323aa6fbce",
            "dm_name": "dm-4",
            "venprod": "DELL,MD36xxi",
            "size": "44T",
            "features": "3 queue_if_no_path pg_init_retries 55",
            "hwhandler": "1 rdac",
            "wp": "rw",
            "path_group": [
                 {
                    "policy": "round-robin 0",
                    "prio": "0"
                    "status": "active"
                    "path": [
                        ['13:0:0:2', 'sdc', '8:32',  'active', 'ready', 'running'],
                        ['14:0:0:2', 'sdi', '8:128', 'active', 'ready', 'running'],
                        ['16:0:0:2', 'sdo', '8:224', 'active', 'ready', 'running'],
                        ['18:0:0:2', 'sdv', '65:80', 'active', 'ready', 'running']
                    ]
                 },
                 {
                    "policy": "round-robin 0",
                    "prio": "0"
                    "status": "enabled"
                    "path": [
                        ['12:0:0:2', 'sdf', '8:80',  'active', 'ready', 'running'],
                        ['11:0:0:2', 'sdl', '8:176', 'active', 'ready', 'running'],
                        ['15:0:0:2', 'sdr', '65:16', 'active', 'ready', 'running'],
                        ['17:0:0:2', 'sdx', '65:112','active', 'ready', 'running']
                    ]
                }
            ]
          }
        ]
    """

    mpath_dev_all = []
    mpath_dev = {}
    path_info = []
    path_group = []
    path_group_attr = {}
    for line in context.content:
        m = MPATH_WWID_REG.search(line)

        if m:
            # Save previous path group info if we have any:
            # Now that we've got a valid path, append the group data if we
            # haven't already
            if path_info:
                path_group_attr['path'] = path_info
                path_group.append(path_group_attr)
                # Must reset path group info to not carry on into new device
                path_group_attr = {}
                path_info = []
                mpath_dev['path_group'] = path_group
                mpath_dev_all.append(mpath_dev)

            mpath_dev = {}
            path_group = []
            wwid = m.group(1)
            no_alias = line.startswith(wwid)
            (dm, venprod) = re.findall(r".*(dm-\S+)\s+(.*)", line)[0]
            if not no_alias:
                (dm, venprod) = re.findall(r"\w+\s+\(.*\)\s+(dm-\S+)\s+(.*)", line)[0]
                mpath_dev['alias'] = line.split()[0]
            mpath_dev['wwid'] = wwid
            mpath_dev['dm_name'] = dm
            mpath_dev['venprod'] = venprod

        elif 'size=' in line:
            if '][' in line:
                # Old RHEL 5 format:
                for (k, v) in PROPERTY_SQBRKT_REG.findall(line):
                    mpath_dev[k] = v
                # Handle un-named write policy attribute on the end:
                mpath_dev['wp'] = line[-3:-1]
            else:
                # Newer RHEL 6 format:
                attr_line = shlex.split(line)
                for item in attr_line:
                    (k, v) = item.split('=', 1)
                    mpath_dev[k] = v

        elif PATHGROUP_POLICY_REG.search(line):
            m = PATHGROUP_POLICY_REG.search(line)
            # New path info - save the previous if we have one:
            if path_info:
                path_group_attr['path'] = path_info
                path_group.append(path_group_attr)

            path_group_attr = {}
            path_info = []
            path_group_attr['policy'] = m.group('policy')
            path_group_attr['prio'] = m.group('priority')
            path_group_attr['status'] = m.group('status')

        elif HCTL_REG.search(line):
            colon_index = line.index(":")
            # Dodgy hack to convert RHEL 5 attributes in square brackets into
            # spaced out words to combine into the list
            line = line.replace('[', ' ').replace(']', ' ')
            path_info.append(line[colon_index - 2:].split())

    # final save of outstanding path and path group data:
    if path_info:
        path_group_attr['path'] = path_info
        path_group.append(path_group_attr)
    if path_group:
        mpath_dev['path_group'] = path_group
        mpath_dev_all.append(mpath_dev)

    return mpath_dev_all
