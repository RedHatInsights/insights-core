# -*- coding: UTF-8 -*-
from falafel.core import FileListing
from falafel.tests import context_wrap

import unittest

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
drwxr-xr-x+  2 0 0       41 Jul  6 23:32 additional_ACLs
-rw-rw----.  1 0 6 253,  10 Aug  4 16:56 comma in size currently valid
brw-rw----.  1 0 6  1048576 Aug  4 16:56 block dev with no comma also valid
-rwxr-xr-x.  2 0 0     1024 Jul  6 23:32 file_name_ending_with_colon:
lrwxrwxrwx.  1 0 0       11 Aug  4  2014 link with spaces -> ../file with spaces
"""

SELINUX_DIRECTORY = """
/boot:
total 3
-rw-r--r--. root root system_u:object_r:boot_t:s0      config-3.10.0-267
drwxr-xr-x. root root system_u:object_r:boot_t:s0      grub2
-rw-r--r--. root root system_u:object_r:boot_t:s0      initramfs-0-rescue
"""

FILES_CREATED_WITH_SELINUX_DISABLED = """
/dev/mapper:
total 2
lrwxrwxrwx 1 0 0 7 Apr 27 05:34 lv_cpwtk001_data01 -> ../dm-7
lrwxrwxrwx 1 0 0 7 Apr 27 05:34 lv_cpwtk001_redo01 -> ../dm-8
"""

BAD_DIRECTORY_ENTRIES = """
dr-xr-xr-x.  2 0 0     4096 Mar  4 16:19 dir entry with no dir header
total 3

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
-rw------ 1 root root 762 Sep 23 002 permission too short
bash: ls: command not found
-rw------ 1 root root 762 Se
-rw------- 1 ro:t root 762 Sep 23 002 colon in uid
-rw------- 1 root r:ot 762 Sep 23 002 colon in gid
-rwasdfas- 1 root root 762 Sep 23 002 bad permissions block
-rwx/----- 1 root root 762 Sep 23 002 slash in permissions block
-rwx------ 1 root root 762 Sep 23 002 /slashes/in/filename
/rwasdfas- 1 root root 762 Sep 23 002 slash in file type and no colon on end
/usr/bin/ls: cannot access /boot/grub2/grub.cfg: No such file or directory
cannot access /boot/grub2/grub.cfg: No such file or directory
No such file or directory
adsf
"""

# Note - should we test for anomalous but parseable entries?  E.g. block
# devices without a major/minor number?  Or non-devices that have a comma in
# the size?  Permissions that don't make sense?  Dates that don't make sense
# but still fit the patterns?  What should the parser do with such entries?


class TestFileListing(unittest.TestCase):
    def test_multiple_directories(self):
        dirs = FileListing(context_wrap(MULTIPLE_DIRECTORIES))

        self.assertIn('/etc/sysconfig', dirs)
        self.assertIn('/etc/sysconfig', dirs.listings)
        self.assertIn('/etc/rc.d/rc3.d', dirs)
        self.assertNotIn('/etc/rc.d/rc4.d', dirs)

        esc = dirs.listings['/etc/sysconfig']
        self.assertEqual(
            sorted(esc.keys()),
            sorted(['entries', 'files', 'dirs', 'specials', 'total', 'raw_list', 'name'])
        )

        self.assertEqual(dirs.files_of('/etc/sysconfig'),
                         ['ebtables-config', 'firewalld', 'grub'])
        self.assertEqual(dirs.dirs_of('/etc/sysconfig'), ['.', '..', 'cbq', 'console'])
        self.assertEqual(dirs.specials_of('/etc/sysconfig'), [])

        # Testing the main features
        listing = dirs.listing_of('/etc/sysconfig')
        self.assertEqual(listing['..'],
                         {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 77, 'owner': '0',
                          'group': '0', 'size': 8192, 'date': 'Jul 13 03:55', 'name': '..',
                          'raw_entry': 'drwxr-xr-x. 77 0 0 8192 Jul 13 03:55 ..',
                          'dir': '/etc/sysconfig'})
        self.assertEqual(listing['cbq'],
                         {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 2, 'owner': '0',
                          'group': '0', 'size': 41, 'date': 'Jul  6 23:32', 'name': 'cbq',
                          'raw_entry': 'drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq',
                          'dir': '/etc/sysconfig'})
        self.assertEqual(listing['firewalld'],
                         {'type': '-', 'perms': 'rw-r--r--.', 'links': 1, 'owner': '0',
                          'group': '0', 'size': 72, 'date': 'Sep 15  2015',
                          'name': 'firewalld', 'raw_entry':
                              '-rw-r--r--.  1 0 0   72 Sep 15  2015 firewalld',
                          'dir': '/etc/sysconfig'})
        self.assertEqual(listing['grub'],
                         {'type': 'l', 'perms': 'rwxrwxrwx.', 'links': 1, 'owner': '0',
                          'group': '0', 'size': 17, 'date': 'Jul  6 23:32', 'name': 'grub',
                          'link': '/etc/default/grub', 'raw_entry':
                              'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub',
                          'dir': '/etc/sysconfig'})

        listing = dirs.listing_of('/etc/rc.d/rc3.d')
        self.assertEqual(listing['..'],
                         {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 10, 'owner': '0',
                          'group': '0', 'size': 4096, 'date': 'Sep 16  2015', 'name': '..',
                          'raw_entry': 'drwxr-xr-x. 10 0 0 4096 Sep 16  2015 ..',
                          'dir': '/etc/rc.d/rc3.d'})
        self.assertEqual(listing['K50netconsole'],
                         {'type': 'l', 'perms': 'rwxrwxrwx.', 'links': 1, 'owner': '0',
                          'group': '0', 'size': 20, 'date': 'Jul  6 23:32',
                          'name': 'K50netconsole', 'link': '../init.d/netconsole', 'raw_entry':
                              'lrwxrwxrwx.  1 0 0   20 Jul  6 23:32 K50netconsole -> ../init.d/netconsole',
                          'dir': '/etc/rc.d/rc3.d'})

        self.assertEqual(dirs.total_of('/etc/sysconfig'), 96)
        self.assertEqual(dirs.total_of('/etc/rc.d/rc3.d'), 4)

        assert dirs.dir_contains('/etc/sysconfig', 'firewalld')
        self.assertEqual(dirs.dir_entry('/etc/sysconfig', 'grub'),
                         {'type': 'l', 'perms': 'rwxrwxrwx.', 'links': 1, 'owner': '0',
                          'group': '0', 'size': 17, 'date': 'Jul  6 23:32', 'name': 'grub',
                          'link': '/etc/default/grub', 'raw_entry':
                              'lrwxrwxrwx.  1 0 0   17 Jul  6 23:32 grub -> /etc/default/grub',
                          'dir': '/etc/sysconfig'})

        self.assertEqual(dirs.raw_directory('/etc/sysconfig'),
                         MULTIPLE_DIRECTORIES.split('\n')[3:10])

        self.assertEqual(dirs.path_entry('/etc/sysconfig/cbq'),
                         {'type': 'd', 'perms': 'rwxr-xr-x.', 'links': 2, 'owner': '0',
                          'group': '0', 'size': 41, 'date': 'Jul  6 23:32', 'name': 'cbq',
                          'raw_entry': 'drwxr-xr-x.  2 0 0   41 Jul  6 23:32 cbq',
                          'dir': '/etc/sysconfig'})
        self.assertIsNone(dirs.path_entry('no_slash'))
        self.assertIsNone(dirs.path_entry('/'))
        self.assertIsNone(dirs.path_entry('/foo'))
        self.assertIsNone(dirs.path_entry('/etc/sysconfig/notfound'))

    def test_complicated_directory(self):
        dirs = FileListing(context_wrap(COMPLICATED_FILES))

        # Test the things we expect to be different:
        listing = dirs.listing_of('/tmp')
        self.assertEqual(listing['config-3.10.0-229.14.1.el7.x86_64']['type'], '-')
        self.assertEqual(listing['menu.lst']['type'], 'l')
        self.assertEqual(listing['menu.lst']['link'], './grub.conf')
        self.assertEqual(dirs.dir_entry('/tmp', 'dm-10'),
                         {'type': 'b', 'perms': 'rw-rw----.', 'links': 1, 'owner': '0',
                          'group': '6', 'major': 253, 'minor': 10, 'date': 'Aug  4 16:56',
                          'name': 'dm-10', 'dir': '/tmp', 'raw_entry':
                              'brw-rw----.  1 0 6 253,  10 Aug  4 16:56 dm-10'})
        self.assertEqual(listing['dm-10']['type'], 'b')
        self.assertEqual(listing['dm-10']['major'], 253)
        self.assertEqual(listing['dm-10']['minor'], 10)
        self.assertEqual(listing['control']['type'], 'c')
        self.assertEqual(listing['control']['major'], 10)
        self.assertEqual(listing['control']['minor'], 236)
        self.assertEqual(listing['geany_socket.c46453c2']['type'], 's')
        self.assertEqual(listing['geany_socket.c46453c2']['size'], 0)
        self.assertEqual(listing['link with spaces']['type'], 'l')
        self.assertEqual(listing['link with spaces']['link'], '../file with spaces')

        # Check that things that _shouldn't_ be there _aren't_
        self.assertNotIn('size', listing['dm-10'])
        self.assertNotIn('size', listing['control'])

        # Tricky file names
        self.assertIn('File name with spaces in it!', listing)
        self.assertIn('Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt', listing)
        self.assertIn('file_name_ending_with_colon:', listing)
        self.assertTrue(dirs.dir_contains('/tmp', 'File name with spaces in it!'))
        assert dirs.dir_contains('/tmp', 'Unicode ÅÍÎÏÓÔÒÚÆ☃ madness.txt')
        assert dirs.dir_contains('/tmp', 'file_name_ending_with_colon:')

        # Grey area - commas in size for ordinary files, and devices without
        # major or minor numbers
        self.assertIn('comma in size currently valid', listing)
        # For ordinary files, commas in size leave size unconverted
        self.assertEqual(listing['comma in size currently valid']['size'], '253,  10')
        self.assertNotIn('major', listing['comma in size currently valid'])
        self.assertNotIn('minor', listing['comma in size currently valid'])
        # For devices missing a comma in their 'size', size is also unconverted
        self.assertIn('block dev with no comma also valid', listing)
        self.assertEqual(listing['block dev with no comma also valid']['size'], '1048576')
        self.assertNotIn('major', listing['block dev with no comma also valid'])
        self.assertNotIn('minor', listing['block dev with no comma also valid'])

        # Extended ACLs
        self.assertIn('additional_ACLs', listing)
        self.assertEqual(listing['additional_ACLs']['perms'], 'rwxr-xr-x+')

    def test_selinux_directory(self):
        dirs = FileListing(context_wrap(SELINUX_DIRECTORY), selinux=True)

        # Test that one entry is exactly what we expect it to be.
        self.assertEqual(dirs.dir_entry('/boot', 'grub2'),
                         {'type': 'd', 'perms': 'rwxr-xr-x.', 'owner': 'root', 'group': 'root',
                          'se_user': 'system_u', 'se_role': 'object_r', 'se_type': 'boot_t',
                          'se_mls': 's0', 'name': 'grub2', 'raw_entry':
                              'drwxr-xr-x. root root system_u:object_r:boot_t:s0      grub2',
                          'dir': '/boot'})

    def test_files_created_with_selinux_disabled(self):
        dirs = FileListing(context_wrap(FILES_CREATED_WITH_SELINUX_DISABLED))

        # Test that one entry is exactly what we expect it to be.
        self.assertEqual(dirs.dir_entry('/dev/mapper', 'lv_cpwtk001_data01'),
                         {'group': '0', 'name': 'lv_cpwtk001_data01', 'links': 1, 'perms': 'rwxrwxrwx',
                          'raw_entry': 'lrwxrwxrwx 1 0 0 7 Apr 27 05:34 lv_cpwtk001_data01 -> ../dm-7', 'owner': '0',
                          'link': '../dm-7', 'date': 'Apr 27 05:34', 'type': 'l', 'dir': '/dev/mapper', 'size': 7})

    def test_bad_directory(self):
        dirs = FileListing(context_wrap(BAD_DIRECTORY_ENTRIES))

        # None of those entries should parse.  So we should have the raw lines,
        # but no parsed entries
        bad_listing = [s.strip() for s in BAD_DIRECTORY_ENTRIES.split('\n')[5:] if s]
        self.assertEqual(dirs.raw_directory('/badness'), bad_listing)
        self.assertEqual(dirs.listing_of('/badness'), {})
