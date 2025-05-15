import doctest

from insights.parsers import ls_dev
from insights.parsers.ls_dev import LsDev
from insights.tests import context_wrap

LS_DEV = """
/dev:
total 3
brw-rw----.  1 0  6 253,   0 Aug  4 16:56 dm-0
brw-rw----.  1 0  6 253,   1 Aug  4 16:56 dm-1
brw-rw----.  1 0  6 253,  10 Aug  4 16:56 dm-10
crw-rw-rw-.  1 0  5   5,   2 Aug  5  2016 ptmx
drwxr-xr-x.  2 0  0        0 Aug  4 16:56 pts
lrwxrwxrwx.  1 0  0       25 Oct 25 14:48 initctl -> /run/systemd/initctl/fifo

/dev/rhel:
total 0
drwxr-xr-x.  2 0 0  100 Jul 25 10:00 .
drwxr-xr-x. 23 0 0 3720 Jul 25 12:43 ..
lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 home -> ../dm-2
lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 root -> ../dm-0
lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 swap -> ../dm-1

/dev/mapper:
total 0
drwxr-xr-x.  2 0 0     140 Jul 25 10:00 .
drwxr-xr-x. 23 0 0    3720 Jul 25 12:43 ..
crw-------.  1 0 0 10, 236 Jul 25 10:00 control
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 docker-253:0-1443032-pool -> ../dm-3
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 rhel-home -> ../dm-2
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 rhel-root -> ../dm-0
lrwxrwxrwx.  1 0 0       7 Jul 25 10:00 rhel-swap -> ../dm-1
"""

LS_ALZR_DEV = """
/dev:
total 0
drwxr-xr-x. 19 root     root    system_u:object_r:device_t:s0                  3300 Sep 30 16:58 .
dr-xr-xr-x. 18 root     root    system_u:object_r:root_t:s0                     235 Apr 21  2023 ..
crw-r--r--.  1 root     root    system_u:object_r:autofs_device_t:s0        10, 235 Sep 30 16:58 autofs
drwxr-xr-x.  2 root     root    system_u:object_r:device_t:s0                   180 Sep 30 16:58 block
lrwxrwxrwx.  1 root     root    system_u:object_r:device_t:s0                    12 Sep 30 16:58 initctl -> /run/initctl
brw-rw----.  1 root     disk    system_u:object_r:fixed_disk_device_t:s0   252,   0 Sep 30 16:58 vda
brw-rw----.  1 root     disk    system_u:object_r:fixed_disk_device_t:s0   252,   1 Sep 30 16:58 vda1
brw-rw----.  1 root     disk    system_u:object_r:fixed_disk_device_t:s0   252,   2 Sep 30 16:58 vda2

/dev/mapper:
total 0
drwxr-xr-x.  2 root root system_u:object_r:device_t:s0          100 Sep 30 16:58 .
drwxr-xr-x. 19 root root system_u:object_r:device_t:s0         3300 Sep 30 16:58 ..
crw-------.  1 root root system_u:object_r:lvm_control_t:s0 10, 236 Sep 30 16:58 control
lrwxrwxrwx.  1 root root system_u:object_r:device_t:s0            7 Sep 30 16:58 rhel-root -> ../dm-0
lrwxrwxrwx.  1 root root system_u:object_r:device_t:s0            7 Sep 30 16:58 rhel-swap -> ../dm-1

/dev/rhel:
total 0
drwxr-xr-x.  2 root root system_u:object_r:device_t:s0   80 Sep 30 16:58 .
drwxr-xr-x. 19 root root system_u:object_r:device_t:s0 3300 Sep 30 16:58 ..
lrwxrwxrwx.  1 root root system_u:object_r:device_t:s0    7 Sep 30 16:58 root -> ../dm-0
lrwxrwxrwx.  1 root root system_u:object_r:device_t:s0    7 Sep 30 16:58 swap -> ../dm-1
"""


def test_ls_dev():
    lsdev = LsDev(context_wrap(LS_DEV))
    assert lsdev.listing_of("/dev/rhel") == {
        "home": {
            "group": "0",
            "name": "home",
            "links": 1,
            "perms": "rwxrwxrwx.",
            "owner": "0",
            "link": "../dm-2",
            "date": "Jul 25 10:00",
            "type": "l",
            "size": 7,
            "dir": "/dev/rhel",
        },
        "root": {
            "group": "0",
            "name": "root",
            "links": 1,
            "perms": "rwxrwxrwx.",
            "owner": "0",
            "link": "../dm-0",
            "date": "Jul 25 10:00",
            "type": "l",
            "size": 7,
            "dir": "/dev/rhel",
        },
        "swap": {
            "group": "0",
            "name": "swap",
            "links": 1,
            "perms": "rwxrwxrwx.",
            "owner": "0",
            "link": "../dm-1",
            "date": "Jul 25 10:00",
            "type": "l",
            "size": 7,
            "dir": "/dev/rhel",
        },
        "..": {
            "group": "0",
            "name": "..",
            "links": 23,
            "perms": "rwxr-xr-x.",
            "owner": "0",
            "date": "Jul 25 12:43",
            "type": "d",
            "size": 3720,
            "dir": "/dev/rhel",
        },
        ".": {
            "group": "0",
            "name": ".",
            "links": 2,
            "perms": "rwxr-xr-x.",
            "owner": "0",
            "date": "Jul 25 10:00",
            "type": "d",
            "size": 100,
            "dir": "/dev/rhel",
        },
    }
    expected = ["docker-253:0-1443032-pool", "rhel-home", "rhel-root", "rhel-swap"]
    actual = lsdev.files_of("/dev/mapper")
    assert actual == expected

    assert lsdev.get("/dev/mapper")["entries"]["rhel-home"]["link"] == "../dm-2"

    ls_alzr_dev = LsDev(context_wrap(LS_ALZR_DEV))
    assert "/dev/rhel" in ls_alzr_dev
    assert ls_alzr_dev.files_of("/dev") == ["initctl"]
    assert ls_alzr_dev.get("/dev")["specials"] == ["autofs", "vda", "vda1", "vda2"]
    assert ls_alzr_dev.get("/dev/rhel")["entries"].get("root") == {
        "type": "l",
        "perms": "rwxrwxrwx.",
        "links": 1,
        "owner": "root",
        "group": "root",
        "size": 7,
        "se_user": "system_u",
        "se_role": "object_r",
        "se_type": "device_t",
        "se_mls": "s0",
        "name": "root",
        "date": "Sep 30 16:58",
        "link": "../dm-0",
        "dir": "/dev/rhel",
    }
    assert (
        ls_alzr_dev.raw_entry_of("/dev/rhel", "root")
        == "lrwxrwxrwx. 1 root root system_u:object_r:device_t:s0 7 Sep 30 16:58 root -> ../dm-0"
    )


def test_doc_examples():
    env = {"ls_dev": LsDev(context_wrap(LS_DEV))}
    failed, total = doctest.testmod(ls_dev, globs=env)
    assert failed == 0
