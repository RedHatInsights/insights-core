import doctest

from insights.parsers import ls_osroot
from insights.parsers.ls_osroot import LsOsroot
from insights.tests import context_wrap

LS_LAN_OSROOT = """
total 5256
dr-xr-xr-x.  17 0 0     271 Apr  5 18:08 .
dr-xr-xr-x.  17 0 0     271 Apr  5 18:08 ..
-rw-r--r--.   1 0 0       0 Feb 25  2017 1
lrwxrwxrwx.   1 0 0       7 Feb 25  2017 bin -> usr/bin
dr-xr-xr-x.   3 0 0    4096 Feb 25  2017 boot
-rw-r--r--.   1 0 0 5168141 Oct 16  2017 channel-list
drwxr-xr-x.  21 0 0    3440 Apr 12 14:46 dev
drwxr-xr-x. 148 0 0    8192 Apr 18 09:17 etc
drwxr-xr-x.   5 0 0      37 Jul 31  2017 home
lrwxrwxrwx.   1 0 0       7 Feb 25  2017 lib -> usr/lib
lrwxrwxrwx.   1 0 0       9 Feb 25  2017 lib64 -> usr/lib64
drwxr-xr-x.   2 0 0       6 Mar 10  2016 media
drwxr-xr-x.   2 0 0       6 Mar 10  2016 mnt
drwxr-xr-x.   5 0 0      48 Mar 27 13:37 opt
dr-xr-xr-x. 265 0 0       0 Apr  6 02:07 proc
-rw-r--r--.   1 0 0  175603 Apr  5 18:08 .readahead
dr-xr-x---.  26 0 0    4096 Apr 18 09:17 root
drwxr-xr-x.  43 0 0    1340 Apr 18 09:17 run
lrwxrwxrwx.   1 0 0       8 Feb 25  2017 sbin -> usr/sbin
drwxr-xr-x.   2 0 0       6 Mar 10  2016 srv
dr-xr-xr-x.  13 0 0       0 Apr  5 18:07 sys
drwxrwxrwt.  40 0 0    8192 Apr 18 11:17 tmp
drwxr-xr-x.  13 0 0     155 Feb 25  2017 usr
drwxr-xr-x.  21 0 0    4096 Apr  6 02:07 var
""".strip()


def test_ls_osroot():
    ls_osroot = LsOsroot(context_wrap(LS_LAN_OSROOT, path='ls_-lan'))
    assert '/' in ls_osroot
    assert len(ls_osroot.files_of("/")) == 7
    assert ls_osroot.files_of("/") == ['1', 'bin', 'channel-list', 'lib', 'lib64', '.readahead', 'sbin']
    assert ls_osroot.dirs_of("/") == ['.', '..', 'boot', 'dev', 'etc', 'home', 'media', 'mnt', 'opt', 'proc', 'root', 'run', 'srv', 'sys', 'tmp', 'usr', 'var']
    assert ls_osroot.listing_of("/")['tmp'] == {'group': '0', 'name': 'tmp', 'links': 40, 'perms': 'rwxrwxrwt.', 'raw_entry': 'drwxrwxrwt.  40 0 0    8192 Apr 18 11:17 tmp', 'owner': '0', 'date': 'Apr 18 11:17', 'type': 'd', 'dir': '/', 'size': 8192}


def test_ls_osroot_doc_examples():
    env = {
        'LsOsroot': LsOsroot,
        'ls_osroot': LsOsroot(context_wrap(LS_LAN_OSROOT, path='ls_-lan')),
    }
    failed, total = doctest.testmod(ls_osroot, globs=env)
    assert failed == 0
