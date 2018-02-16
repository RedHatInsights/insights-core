from insights.parsers import multipath_v4_ll
from insights.tests import context_wrap
import doctest

MULTIPATH_V4_LL_INFO = """
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
size=44T features='3 queue_if_no_path pg_init_retries 55' hwhandler='2 rdac' wp=rx
|-+- policy='round-robin 0' prio=1 status=active
| |- 12:0:0:2 sdc 8:32   active ready running
| |- 11:0:0:2 sdi 8:128  active ready running
| |- 15:0:0:2 sdo 8:224  active ready running
| `- 17:0:0:2 sdv 65:80  active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  |- 13:0:0:2 sdf 8:80   active ready running
  |- 14:0:0:2 sdl 8:176  active ready running
  |- 16:0:0:2 sdr 65:16  active ready running
  `- 18:0:0:2 sdx 65:112 active ready running
36001405b1629f80d52a4c898f8856e43 dm-5 LIO-ORG ,block0_sdb
size=2.0G features='0' hwhandler='0' wp=rw
|-+- policy='service-time 0' prio=1 status=active
| `- 3:0:0:0 sdc 8:32 active ready running
`-+- policy='service-time 0' prio=1 status=enabled
  `- 4:0:0:0 sdb 8:16 active ready running
mpatha (1IET     00080001) dm-0 IET,VIRTUAL-DISK
size=16G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 3:0:0:1 sdb 8:16 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  `- 4:0:0:1 sdc 8:32 active ready running
1IET     00080001 dm-0 IET,VIRTUAL-DISK
size=16G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 3:0:0:1 sdb 8:16 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  `- 4:0:0:1 sdc 8:32 active ready running
mpathb (1IET     00080002) dm-8 COMPELNT,Compellent Vol
size=16G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 3:0:0:1 sdb 8:16 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  `- 4:0:0:1 sdc 8:32 active ready running
1IET     00080007 dm-19 COMPELNT,Compellent Vol
size=16G features='0' hwhandler='0' wp=rw
|-+- policy='round-robin 0' prio=1 status=active
| `- 3:0:0:1 sdb 8:16 active ready running
`-+- policy='round-robin 0' prio=1 status=enabled
  `- 4:0:0:1 sdc 8:32 active ready running
mpathc (test_with_no_devs) dm-1 uninitialized
size=10G features='0' hwhandler='0' wp=rw
""".strip()

MULTIPATH_V4_LL_INFO_RHEL_5 = """
sdz: size = 293601280
sdz: vendor = DGC
sdz: product = RAID 5
sdz: rev = 0430
sdz: h:b:t:l = 5:0:1:6
sdz: tgt_node_name = 0x50060160c4603569
sdz: path checker = emc_clariion (controller setting)
sdz: checker timeout = 60000 ms (sysfs setting)
sdz: state = 2
sr0: blacklisted
sr1: blacklisted
===== paths list =====
uuid hcil    dev  dev_t  pri dm_st  chk_st  vend/prod/rev
     5:0:1:7 sdaa 65:160 0   [undef][ready] DGC,RAID 5
     3:0:0:5 sdab 65:176 0   [undef][ready] DGC,RAID 5
     3:0:0:6 sdac 65:192 0   [undef][ready] DGC,RAID 5
     3:0:0:7 sdad 65:208 0   [undef][ready] DGC,RAID 5
     3:0:1:5 sdae 65:224 0   [undef][ready] DGC,RAID 5
     3:0:1:6 sdaf 65:240 0   [undef][ready] DGC,RAID 5
     3:0:1:7 sdag 66:0   0   [undef][ready] DGC,RAID 5
     0:2:0:0 sda  8:0    0   [undef][ready] DELL,PERC 6/i
     3:0:0:0 sdb  8:16   0   [undef][ready] DGC,RAID 5
     3:0:0:1 sdc  8:32   0   [undef][ready] DGC,RAID 5
     3:0:0:2 sdd  8:48   0   [undef][ready] DGC,RAID 5
     3:0:0:3 sde  8:64   0   [undef][ready] DGC,RAID 5
     3:0:0:4 sdf  8:80   0   [undef][ready] DGC,RAID 5
     3:0:1:0 sdg  8:96   0   [undef][ready] DGC,RAID 5
     3:0:1:1 sdh  8:112  0   [undef][ready] DGC,RAID 5
     3:0:1:2 sdi  8:128  0   [undef][ready] DGC,RAID 5
     3:0:1:3 sdj  8:144  0   [undef][ready] DGC,RAID 5
     3:0:1:4 sdk  8:160  0   [undef][ready] DGC,RAID 5
     5:0:0:0 sdl  8:176  0   [undef][ready] DGC,RAID 5
     5:0:0:1 sdm  8:192  0   [undef][ready] DGC,RAID 5
     5:0:0:2 sdn  8:208  0   [undef][ready] DGC,RAID 5
     5:0:0:3 sdo  8:224  0   [undef][ready] DGC,RAID 5
     5:0:0:4 sdp  8:240  0   [undef][ready] DGC,RAID 5
     5:0:1:0 sdq  65:0   0   [undef][ready] DGC,RAID 5
     5:0:1:1 sdr  65:16  0   [undef][ready] DGC,RAID 5
     5:0:1:2 sds  65:32  0   [undef][ready] DGC,RAID 5
     5:0:1:3 sdt  65:48  0   [undef][ready] DGC,RAID 5
     5:0:1:4 sdu  65:64  0   [undef][ready] DGC,RAID 5
     5:0:0:5 sdv  65:80  0   [undef][ready] DGC,RAID 5
     5:0:0:6 sdw  65:96  0   [undef][ready] DGC,RAID 5
     5:0:0:7 sdx  65:112 0   [undef][ready] DGC,RAID 5
     5:0:1:5 sdy  65:128 0   [undef][ready] DGC,RAID 5
     5:0:1:6 sdz  65:144 0   [undef][ready] DGC,RAID 5
params = 1 queue_if_no_path 1 emc 2 1 round-robin 0 2 1 8:160 1000 8:240 1000 round-robin 0 2 1 8:80 1000 65:64 1000
status = 2 0 1 0 2 1 A 0 2 0 8:160 A 0 8:240 A 0 E 0 2 0 8:80 A 0 65:64 A 0
*word = 1, len = 1
*word = queue_if_no_path, len = 16
*word = 1, len = 1
*word = emc, len = 3
sdu: getprio = /sbin/mpath_prio_emc /dev/%n (controller setting)
process 31154 forking to exec '/sbin/mpath_prio_emc /dev/sdu' ((nil))
forked 31158
sdu: prio = 0
*word = 2, len = 1
*word = 1, len = 1
L004 (360060160ade32800f2e3baf47665e211) dm-9 DGC,RAID 5
[size=100G][features=1 queue_if_no_path][hwhandler=1 emc][rw]
\_ round-robin 0 [prio=1][active]
 \_ 3:0:1:4 sdk  8:160  [active][ready]
 \_ 5:0:0:4 sdp  8:240  [active][ready]
\_ round-robin 0 [prio=0][enabled]
 \_ 3:0:0:4 sdf  8:80   [active][ready]
 \_ 5:0:1:4 sdu  65:64  [active][ready]
params = 1 queue_if_no_path 1 emc 2 1 round-robin 0 2 1 8:64 1000 65:48 1000 round-robin 0 2 1 8:144 1000 8:224 1000
status = 2 0 1 0 2 1 A 0 2 0 8:64 A 0 65:48 A 0 E 0 2 0 8:144 A 0 8:224 A 0
*word = 1, len = 1
*word = queue_if_no_path, len = 16
"""


def test_class_RHEL6():
    mp = multipath_v4_ll.MultipathDevices(context_wrap(MULTIPATH_V4_LL_INFO))
    assert len(mp.devices) == 7
    assert mp.devices[0] == {
        "alias": "mpathg",
        "wwid": "36f01faf000da360b0000033c528fea6d",
        "dm_name": "dm-2",
        "venprod": "DELL,MD36xxi",
        "size": "54T",
        "features": "3 queue_if_no_path pg_init_retries 50",
        "hwhandler": "1 rdac",
        "wp": "rw",
        "path_group": [{
            "policy": "round-robin 0",
            "prio": "0",
            "status": "active",
            "path": [
                ['12:0:0:1', 'sdc', '8:32', 'active', 'ready', 'running'],
                ['11:0:0:1', 'sdi', '8:128', 'active', 'ready', 'running'],
                ['15:0:0:1', 'sdo', '8:224', 'active', 'ready', 'running'],
                ['17:0:0:1', 'sdv', '65:80', 'active', 'ready', 'running']
            ]
        }, {
            "policy": "round-robin 0",
            "prio": "0",
            "status": "enabled",
            "path": [
                ['13:0:0:1', 'sdf', '8:80', 'active', 'ready', 'running'],
                ['14:0:0:1', 'sdl', '8:176', 'active', 'ready', 'running'],
                ['16:0:0:1', 'sdr', '65:16', 'active', 'ready', 'running'],
                ['18:0:0:1', 'sdx', '65:112', 'active', 'ready', 'running']
            ]
        }]
    }
    assert mp.devices[0].get('size') == '54T'
    assert mp.devices[1].get('path_group') == [{
        "policy": "round-robin 0",
        "prio": "1",
        "status": "active",
        "path": [
            ['12:0:0:2', 'sdc', '8:32', 'active', 'ready', 'running'],
            ['11:0:0:2', 'sdi', '8:128', 'active', 'ready', 'running'],
            ['15:0:0:2', 'sdo', '8:224', 'active', 'ready', 'running'],
            ['17:0:0:2', 'sdv', '65:80', 'active', 'ready', 'running']
        ]
    }, {
        "policy": "round-robin 0",
        "prio": "1",
        "status": "enabled",
        "path": [
            ['13:0:0:2', 'sdf', '8:80', 'active', 'ready', 'running'],
            ['14:0:0:2', 'sdl', '8:176', 'active', 'ready', 'running'],
            ['16:0:0:2', 'sdr', '65:16', 'active', 'ready', 'running'],
            ['18:0:0:2', 'sdx', '65:112', 'active', 'ready', 'running']
        ]
    }]
    assert mp.devices[2].get('hwhandler') == "0"
    assert mp.devices[3].get('alias') == "mpatha"
    assert mp.devices[4].get('wwid') == "1IET     00080001"
    assert mp.devices[5].get('venprod') == "COMPELNT,Compellent Vol"
    assert mp.devices[5].get('dm_name') == "dm-8"
    assert mp.devices[6].get('venprod') == "COMPELNT,Compellent Vol"
    assert mp.devices[6].get('dm_name') == "dm-19"
    # Note that there's no data for the made-up 'mpathc', since there's no
    # path group information and only devices with path group information
    # get saved.
    assert mp.dms == ['dm-2', 'dm-4', 'dm-5', 'dm-0', 'dm-0', 'dm-8', 'dm-19']
    assert mp.by_dm['dm-2'] == mp.devices[0]
    assert mp.aliases == ['mpathg', 'mpathe', 'mpatha', 'mpathb']
    assert mp.by_alias['mpathg'] == mp.devices[0]
    assert mp.wwids == [
        '36f01faf000da360b0000033c528fea6d',
        '36f01faf000da3761000004323aa6fbce',
        '36001405b1629f80d52a4c898f8856e43',
        '1IET     00080001',
        '1IET     00080001',
        '1IET     00080002',
        '1IET     00080007'
    ]
    assert mp.by_wwid['1IET     00080001'] == mp.devices[4]

    # Pseudo list accessors
    assert len(mp) == 7
    for i, item in enumerate(mp):
        assert item == mp.devices[i]
        assert item == mp[i]


def test_get_multipath_v4_ll():
    multipath_v4_ll_list = multipath_v4_ll.get_multipath_v4_ll(context_wrap(MULTIPATH_V4_LL_INFO))
    assert len(multipath_v4_ll_list) == 7
    assert multipath_v4_ll_list[0] == {
        "alias": "mpathg",
        "wwid": "36f01faf000da360b0000033c528fea6d",
        "dm_name": "dm-2",
        "venprod": "DELL,MD36xxi",
        "size": "54T",
        "features": "3 queue_if_no_path pg_init_retries 50",
        "hwhandler": "1 rdac",
        "wp": "rw",
        "path_group": [{
            "policy": "round-robin 0",
            "prio": "0",
            "status": "active",
            "path": [
                ['12:0:0:1', 'sdc', '8:32', 'active', 'ready', 'running'],
                ['11:0:0:1', 'sdi', '8:128', 'active', 'ready', 'running'],
                ['15:0:0:1', 'sdo', '8:224', 'active', 'ready', 'running'],
                ['17:0:0:1', 'sdv', '65:80', 'active', 'ready', 'running']
            ]
        }, {
            "policy": "round-robin 0",
            "prio": "0",
            "status": "enabled",
            "path": [
                ['13:0:0:1', 'sdf', '8:80', 'active', 'ready', 'running'],
                ['14:0:0:1', 'sdl', '8:176', 'active', 'ready', 'running'],
                ['16:0:0:1', 'sdr', '65:16', 'active', 'ready', 'running'],
                ['18:0:0:1', 'sdx', '65:112', 'active', 'ready', 'running']
            ]
        }]
    }
    assert multipath_v4_ll_list[0].get('size') == '54T'
    assert multipath_v4_ll_list[1].get('path_group') == [{
        "policy": "round-robin 0",
        "prio": "1",
        "status": "active",
        "path": [
            ['12:0:0:2', 'sdc', '8:32', 'active', 'ready', 'running'],
            ['11:0:0:2', 'sdi', '8:128', 'active', 'ready', 'running'],
            ['15:0:0:2', 'sdo', '8:224', 'active', 'ready', 'running'],
            ['17:0:0:2', 'sdv', '65:80', 'active', 'ready', 'running']
        ]
    }, {
        "policy": "round-robin 0",
        "prio": "1",
        "status": "enabled",
        "path": [
            ['13:0:0:2', 'sdf', '8:80', 'active', 'ready', 'running'],
            ['14:0:0:2', 'sdl', '8:176', 'active', 'ready', 'running'],
            ['16:0:0:2', 'sdr', '65:16', 'active', 'ready', 'running'],
            ['18:0:0:2', 'sdx', '65:112', 'active', 'ready', 'running']
        ]
    }]
    assert multipath_v4_ll_list[2].get('hwhandler') == "0"
    assert multipath_v4_ll_list[3].get('alias') == "mpatha"
    assert multipath_v4_ll_list[4].get('wwid') == "1IET     00080001"
    assert multipath_v4_ll_list[5].get('venprod') == "COMPELNT,Compellent Vol"
    assert multipath_v4_ll_list[5].get('dm_name') == "dm-8"
    assert multipath_v4_ll_list[6].get('venprod') == "COMPELNT,Compellent Vol"
    assert multipath_v4_ll_list[6].get('dm_name') == "dm-19"
    # Note that there's no data for the made-up 'mpathc', since there's no
    # path group information and only devices with path group information
    # get saved.


def test_get_multipath_v4_ll_RHEL_5():
    """
    Test alternate device line prefixes, and ignoring extra clutter in input.
    """
    multipath_v4_ll_list = multipath_v4_ll.get_multipath_v4_ll(context_wrap(MULTIPATH_V4_LL_INFO_RHEL_5))

    assert len(multipath_v4_ll_list) == 1

    """
L004 (360060160ade32800f2e3baf47665e211) dm-9 DGC,RAID 5
[size=100G][features=1 queue_if_no_path][hwhandler=1 emc][rw]
\_ round-robin 0 [prio=1][active]
 \_ 3:0:1:4 sdk  8:160  [active][ready]
 \_ 5:0:0:4 sdp  8:240  [active][ready]
\_ round-robin 0 [prio=0][enabled]
 \_ 3:0:0:4 sdf  8:80   [active][ready]
 \_ 5:0:1:4 sdu  65:64  [active][ready]
    """
    path_dev = multipath_v4_ll_list[0]
    assert path_dev['alias'] == 'L004'
    assert path_dev['wwid'] == '360060160ade32800f2e3baf47665e211'
    assert path_dev['dm_name'] == 'dm-9'
    assert path_dev['venprod'] == 'DGC,RAID 5'
    assert path_dev['size'] == '100G'
    assert path_dev['features'] == '1 queue_if_no_path'
    assert path_dev['hwhandler'] == '1 emc'
    assert path_dev['wp'] == 'rw'
    assert path_dev['path_group'][0]['policy'] == 'round-robin 0'
    assert path_dev['path_group'][0]['prio'] == '1'
    assert path_dev['path_group'][0]['status'] == 'active'

    assert len(path_dev['path_group'][0]['path']) == 2
    paths = path_dev['path_group'][0]['path']
    assert len(paths) == 2
    assert paths[0] == ['3:0:1:4', 'sdk', '8:160', 'active', 'ready']


MULTIPATH_V4_LL_DOC = """
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
"""


def test_doc_examples():
    env = {
            'MultipathDevices': multipath_v4_ll.MultipathDevices,
            'mpaths': multipath_v4_ll.MultipathDevices(context_wrap(MULTIPATH_V4_LL_DOC)),
          }
    failed, total = doctest.testmod(multipath_v4_ll, globs=env)
    assert failed == 0
