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


def test_ls_dev():
    ls_dev = LsDev(context_wrap(LS_DEV))
    assert ls_dev.listing_of("/dev/rhel") == {
        'home': {'group': '0', 'name': 'home', 'links': 1, 'perms': 'rwxrwxrwx.',
                 'raw_entry': 'lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 home -> ../dm-2',
                 'owner': '0', 'link': '../dm-2', 'date': 'Jul 25 10:00',
                 'type': 'l', 'size': 7, 'dir': '/dev/rhel'},
        'root': {'group': '0', 'name': 'root', 'links': 1, 'perms': 'rwxrwxrwx.',
                 'raw_entry': 'lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 root -> ../dm-0',
                 'owner': '0', 'link': '../dm-0', 'date': 'Jul 25 10:00',
                 'type': 'l', 'size': 7, 'dir': '/dev/rhel'},
        'swap': {'group': '0', 'name': 'swap', 'links': 1, 'perms': 'rwxrwxrwx.',
                 'raw_entry': 'lrwxrwxrwx.  1 0 0    7 Jul 25 10:00 swap -> ../dm-1',
                 'owner': '0', 'link': '../dm-1', 'date': 'Jul 25 10:00',
                 'type': 'l', 'size': 7, 'dir': '/dev/rhel'},
        '..': {'group': '0', 'name': '..', 'links': 23, 'perms': 'rwxr-xr-x.',
               'raw_entry': 'drwxr-xr-x. 23 0 0 3720 Jul 25 12:43 ..',
               'owner': '0', 'date': 'Jul 25 12:43', 'type': 'd', 'size': 3720,
               'dir': '/dev/rhel'},
        '.': {'group': '0', 'name': '.', 'links': 2, 'perms': 'rwxr-xr-x.',
              'raw_entry': 'drwxr-xr-x.  2 0 0  100 Jul 25 10:00 .', 'owner': '0',
              'date': 'Jul 25 10:00', 'type': 'd', 'size': 100, 'dir': '/dev/rhel'}}
    expected = ['docker-253:0-1443032-pool', 'rhel-home', 'rhel-root', 'rhel-swap']
    actual = ls_dev.listings.get("/dev/mapper")['files']
    assert actual == expected

    assert ls_dev.listings.get("/dev/mapper")['entries']['rhel-home']['link'] == "../dm-2"
