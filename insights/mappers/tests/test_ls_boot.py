from insights.mappers.ls_boot import LsBoot
from insights.tests import context_wrap

import unittest

LS_BOOT = """
/boot:
total 187380
dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
dr-xr-xr-x. 19 0 0     4096 Jul 14 09:10 ..
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64

/boot/grub2:
total 36
drwxr-xr-x. 6 0 0  104 Mar  4 16:16 .
dr-xr-xr-x. 3 0 0 4096 Mar  4 16:19 ..
lrwxrwxrwx. 1 0 0   11 Aug  4  2014 menu.lst -> ./grub.cfg
-rw-r--r--. 1 0 0   64 Sep 18  2015 device.map
-rw-r--r--. 1 0 0 7040 Mar 29 13:30 grub.cfg
"""

LS_BOOT_LINKS = """
/boot:
total 187380
-rw-------.  1 root root 19143244 Mar  3 14:31 initramfs-2.6.32-504.el6.x86_64.img
lrwxrwxrwx.  1 root root       40 May 11 11:00 initrd -> initramfs-2.6.32-504.12.2.el6.x86_64.img
lrwxrwxrwx.  1 root root       34 May 11 11:00 vmlinuz -> vmlinuz-2.6.32-504.12.2.el6.x86_64
-rwxr-xr-x.  1 root root  4153904 Sep 16  2014 vmlinuz-2.6.32-504.el6.x86_64
"""


class LsBootTests(unittest.TestCase):
    def test_ls_boot(self):
        ls_boot = LsBoot(context_wrap(LS_BOOT))
        self.assertIn('/boot', ls_boot)
        self.assertIn('/boot/grub2', ls_boot)
        self.assertIn('config-3.10.0-229.14.1.el7.x86_64', ls_boot.files_of('/boot'))
        self.assertIn('menu.lst', ls_boot.files_of('/boot/grub2'))
        self.assertIn('device.map', ls_boot.files_of('/boot/grub2'))
        self.assertIn('grub.cfg', ls_boot.files_of('/boot/grub2'))

        # Note: for the 'data' list, we don't care what order the items are in
        self.assertIn("config-3.10.0-229.14.1.el7.x86_64", ls_boot.data)
        self.assertIn("menu.lst", ls_boot.data)
        self.assertIn("device.map", ls_boot.data)
        self.assertIn("grub.cfg", ls_boot.data)
        self.assertEqual(len(ls_boot.data), 4)

    def test_boot_links(self):
        ls_boot = LsBoot(context_wrap(LS_BOOT_LINKS))
        self.assertIn('/boot', ls_boot)
        self.assertIn('initramfs-2.6.32-504.el6.x86_64.img', ls_boot.files_of('/boot'))
        self.assertIn('initrd', ls_boot.files_of('/boot'))
        self.assertIn('vmlinuz', ls_boot.files_of('/boot'))
        self.assertIn('vmlinuz-2.6.32-504.el6.x86_64', ls_boot.files_of('/boot'))
        # data list gives files even if they're links to missing files
        self.assertIn('initramfs-2.6.32-504.el6.x86_64.img', ls_boot.data)
        self.assertIn('vmlinuz-2.6.32-504.el6.x86_64', ls_boot.data)
        self.assertIn('initrd', ls_boot.data)
        self.assertIn('vmlinuz', ls_boot.data)
