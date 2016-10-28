# -*- coding: UTF-8 -*-
from falafel.core import FileListing
from falafel.tests import context_wrap


MULTIPLE_DIRECTORIES = """
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

COMPLICATED_FILES = """
/tmp:
total 16
dr-xr-xr-x.  2 0 0     4096 Mar  4 16:19 .
dr-xr-xr-x. 10 0 0     4096 Mar  4 16:19 ..
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 menu.lst -> ./grub.conf
brw-rw----.  1 0 6 253,  10 Aug  4 16:56 dm-10
crw-------.  1 0 0 10,  236 Jul 25 10:00 control
srw-------.  1 26214 17738 0 Oct 19 08:48 geany_socket.c46453c2
-rw-rw-r--.  1 24306 24306 13895 Oct 21 15:42 File name with spaces in it!
-rw-rw-r--.  1 24306 24306 13895 Oct 21 15:42 Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt
"""

HUMAN_LISTING = """
/var/lib/setroubleshoot:
total 4.0K
-rw-------. 1 root root    0 Apr 15  2015 email_alert_recipients
-rw-------. 1 root root 3.7K Sep  7  2015 setroubleshoot_database.xml
"""

SELINUX_DIRECTORY = """
/boot:
total 3
-rw-r--r--. root root system_u:object_r:boot_t:s0      config-3.10.0-267.el7.x86_64
drwxr-xr-x. root root system_u:object_r:boot_t:s0      grub2
-rw-r--r--. root root system_u:object_r:boot_t:s0      initramfs-0-rescue-71483baa33934d94a7804a398fed6241.img
"""  # noqa

BAD_DIRECTORY_ENTRIES = """
/badness:
    -rwxr-xr-x. 0 0    1 Sep 12 2010 indented entry
xr-xr--r--. 0 0        1 Sep 12  2010 bad file type
-rxr-xr-x.  0 0        1 Sep 12  2010 missing user w permission
-rwxr-xr-x  0 0        1 Sep 12  2010 missing ACL dot
-rw-r--r--. user with spaces group 2 Oct 3 2011 user with spaces
-rw-r--r--. user group with spaces 2 Oct 3 2011 group with spaces
dr-xr-xr-x. -42 -63 1271 Jan  6  2008 Negative user and group numbers
dr-xr-xr-x. 1 7 123, 124, 125 Jan 6 2008 Three comma blocks in size
brw-rw----. 1 0 6 123456 Aug 4 16:56 two size blocks
prw-rw----. 1000 1000  0  6 2007 Month missing
prw-rw----. 1000 1000  0 No 6 2007 Month too short
prw-rw----. 1000 1000  0 November 6 2007 Month too long
prw-rw----. 1000 1000  0 Nov  2007 Day too long
prw-rw----. 1000 1000  0 Nov 126 2007 Day too long
prw-rw----. 1000 1000  0 Nov 126  Year missing
prw-rw----. 1000 1000  0 Nov 126 20107 Year too long
prw-rw----. 1000 1000  0 Nov 12 :56 Missing hour
prw-rw----. 1000 1000  0 Nov 12 723:56 Hour too long
prw-rw----. 1000 1000  0 Nov 12 23: Missing minute
prw-rw----. 1000 1000  0 Nov 12 23:3 Minute too short
prw-rw----. 1000 1000  0 Nov 12 23:357 Minute too long
"""

# Note - should we test for anomalous but parseable entries?  E.g. block
# devices without a major/minor number?  Or non-devices that have a comma in
# the size?  Permissions that don't make sense?  Dates that don't make sense
# but still fit the patterns?  What should the parser do with such entries?


def test_multiple_directories():
    dirs = FileListing(context_wrap(MULTIPLE_DIRECTORIES))

    assert '/etc/sysconfig' in dirs
    assert '/etc/rc.d/rc3.d' in dirs
    assert '/etc/rc.d/rc4.d' not in dirs

    assert dirs.files_of('/etc/sysconfig') == \
        ['ebtables-config', 'firewalld', 'grub']
    assert dirs.dirs_of('/etc/sysconfig') == ['.', '..', 'cbq', 'console']
    assert dirs.specials_of('/etc/sysconfig') == []

    # Testing the main features
    listing = dirs.listing_of('/etc/sysconfig')
    assert listing['..'] == \
        {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 77, 'owner': '0',
         'group': '0', 'size': 8192, 'date': 'Jul 13 03:55', 'name': '..',
         'raw_entry': 'drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..'}
    assert listing['cbq'] == \
        {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 2, 'owner': '0',
         'group': '0', 'size': 41, 'date': 'Jul  6 23:32', 'name': 'cbq',
         'raw_entry': 'drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq'}
    assert listing['firewalld'] == \
        {'type': '-', 'perms': 'rw-r--r--.', 'links': 1, 'owner': '0',
         'group': '0', 'size': 72, 'date': 'Sep 15  2015',
         'name': 'firewalld', 'raw_entry':
         '-rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld'}
    assert listing['grub'] == \
        {'type': 'l', 'perms': 'rwxrwxrwx.', 'links': 1, 'owner': '0',
         'group': '0', 'size': 17, 'date': 'Jul  6 23:32', 'name': 'grub',
         'link': '/etc/default/grub', 'raw_entry':
         'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub'}

    listing = dirs.listing_of('/etc/rc.d/rc3.d')
    assert listing['..'] == \
        {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 10, 'owner': '0',
         'group': '0', 'size': 4096, 'date': 'Sep 16  2015', 'name': '..',
         'raw_entry': 'drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..'}
    assert listing['K50netconsole'] == \
        {'type': 'l', 'perms': 'rwxrwxrwx.', 'links': 1, 'owner': '0',
         'group': '0', 'size': 20, 'date': 'Jul  6 23:32',
         'name': 'K50netconsole', 'link': '../init.d/netconsole', 'raw_entry':
         'lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole'}

    assert dirs.total_of('/etc/sysconfig') == 96
    assert dirs.total_of('/etc/rc.d/rc3.d') == 4

    assert dirs.dir_contains('/etc/sysconfig', 'firewalld')
    assert dirs.dir_entry('/etc/sysconfig', 'grub') == \
        {'type': 'l', 'perms': 'rwxrwxrwx.', 'links': 1, 'owner': '0',
         'group': '0', 'size': 17, 'date': 'Jul  6 23:32', 'name': 'grub',
         'link': '/etc/default/grub', 'raw_entry':
         'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub'}

    assert dirs.raw_directory('/etc/sysconfig') == \
        MULTIPLE_DIRECTORIES.split('\n')[3:10]


def test_complicated_directory():
    dirs = FileListing(context_wrap(COMPLICATED_FILES))

    # Test the things we expect to be different:
    listing = dirs.listing_of('/tmp')
    assert listing['config-3.10.0-229.14.1.el7.x86_64']['type'] == '-'
    assert listing['menu.lst']['type'] == 'l'
    assert listing['menu.lst']['link'] == './grub.conf'
    assert listing['dm-10']['type'] == 'b'
    assert listing['dm-10']['major'] == 253
    assert listing['dm-10']['minor'] == 10
    assert listing['control']['type'] == 'c'
    assert listing['control']['major'] == 10
    assert listing['control']['minor'] == 236
    assert listing['geany_socket.c46453c2']['type'] == 's'
    assert listing['geany_socket.c46453c2']['size'] == 0

    # Check that things that _shouldn't_ be there _aren't_
    assert 'size' not in listing['dm-10']
    assert 'size' not in listing['control']

    # Tricky file names
    assert 'File name with spaces in it!' in listing
    assert 'Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt' in listing
    assert dirs.dir_contains('/tmp', 'File name with spaces in it!')
    assert dirs.dir_contains('/tmp', 'Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt')


def test_human_listing():
    dirs = FileListing(context_wrap(HUMAN_LISTING))

    dirs.total_of('/var/lib/setroubleshoot') == 4096
    dirs.dir_entry('/var/lib/setroubleshoot', 'email_alert_recipients') == \
        {'type': '-', 'perms': 'rw-------.', 'links': 1, 'owner': 'root',
         'group': 'root', 'size': 0, 'date': 'Apr 15  2015',
         'name': 'email_alert_recipients', 'raw_entry':
         '-rw-------. 1 root root    0 Apr 15  2015 email_alert_recipients'}
    dirs.dir_entry('/var/lib/setroubleshoot', 'setroubleshoot_database.xml') \
        == {'type': '-', 'perms': 'rw-------.', 'links': 1, 'owner': 'root',
            'group': 'root', 'size': int(3.7 * 1024), 'date': 'Sep  7  2015',
            'name': 'setroubleshoot_database.xml', 'raw_entry':
            '-rw-------. 1 root root 3.7K Sep  7  2015 setroubleshoot_database.xml'}


def test_selinux_directory():
    dirs = FileListing(context_wrap(SELINUX_DIRECTORY), selinux=True)

    # Test that one entry is exactly what we expect it to be.
    dirs.dir_entry('/boot', 'grub2') == \
        {'type': 'd', 'perms': 'rwxr-xr-x.', 'owner': 'root', 'group': 'root',
         'se_user': 'system_u', 'se_role': 'object_r', 'se_type': 'boot_t',
         'se_mls': 's0', 'name': 'grub2', 'raw_entry':
         'drwxr-xr-x. root root system_u:object_r:boot_t:s0      grub2'}


def test_bad_directory():
    dirs = FileListing(context_wrap(BAD_DIRECTORY_ENTRIES))

    # None of those entries should parse.  So we should have the raw lines,
    # but no parsed entries
    dirs.raw_directory('/badness') == BAD_DIRECTORY_ENTRIES.split('/n')[2:]
    dirs.listing_of('/badness') == []
