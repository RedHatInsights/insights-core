from falafel.mappers import multipath_v4_ll
from falafel.tests import context_wrap

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
""".strip()


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
