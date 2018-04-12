import doctest

from insights.parsers import ls_etc
from insights.tests import context_wrap


LS_ETC = """
/etc/sysconfig:
total 96
drwxr-xr-x.  7 0 0 4096 Jul  6 23:41 .
drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..
drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq
drwxr-xr-x.  2 0 0    6 Sep 16  2015 console
-rw-------.  1 0 0 1390 Mar  4  2014 ebtables-config
-rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub

/etc/rc.d/rc3.d:
total 4
drwxr-xr-x.  2 0 0   58 Jul  6 23:32 .
drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..
lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole
lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 S10network -> ../init.d/network
lrwxrwxrwx.  1 0 0   15 Jul  6 23:32 S97rhnsd -> ../init.d/rhnsd
"""


def test_ls_etc():
    list_etc = ls_etc.LsEtc(context_wrap(LS_ETC))
    assert "/etc/sysconfig" in list_etc
    assert len(list_etc.files_of("/etc/sysconfig")) == 3
    assert list_etc.files_of("/etc/sysconfig") == ['ebtables-config', 'firewalld', 'grub']
    assert list_etc.dirs_of("/etc/sysconfig") == ['.', '..', 'cbq', 'console']
    assert list_etc.specials_of("/etc/sysconfig") == []
    assert list_etc.total_of("/etc/sysconfig") == 96
    grub = list_etc.dir_entry("/etc/sysconfig", "grub")
    assert grub is not None
    assert grub == {
        'group': '0',
        'name': 'grub',
        'links': 1,
        'perms': 'rwxrwxrwx.',
        'raw_entry': 'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub',
        'owner': '0',
        'link': '/etc/default/grub',
        'date': 'Jul  6 23:32',
        'type': 'l',
        'size': 17,
        'dir': '/etc/sysconfig'}
    assert list_etc.files_of("/etc/rc.d/rc3.d") == ['K50netconsole',
                                                  'S10network', 'S97rhnsd']


def test_ls_etc_documentation():
    failed_count, tests = doctest.testmod(
        ls_etc,
        globs={'ls_etc': ls_etc.LsEtc(context_wrap(LS_ETC))}
    )
    assert failed_count == 0
