import pytest

from insights.core.dr import SkipComponent
from insights.specs.datasources.kdump_initramfs_image import kdump_image
from insights.parsers.ls_boot import LsBoot
from insights.tests import context_wrap

LS_BOOT_WITH_KDUMP = """
/boot:
total 187380
dr-xr-xr-x.  3 0 0      4096 Mar  4 16:19 .
dr-xr-xr-x. 19 0 0      4096 Jul 14 09:10 ..
-rw-r--r--.  1 0 0    123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
drwxr-xr-x.  6 0 0       111 Jun 15 09:51 grub2
-rw-------.  1 0 0 105730050 May 12 17:27 initramfs-0-rescue-6bdaf92aa0754b53acbb1dbff7127e2b.img
-rw-------.  1 0 0  55162915 May 12 17:35 initramfs-4.18.0-240.el8.x86_64.img
-rw-------.  1 0 0  19357165 May 13 10:00 initramfs-4.18.0-240.el8.x86_64kdump.img

/boot/grub2:
total 36
drwxr-xr-x. 6 0 0  104 Mar  4 16:16 .
dr-xr-xr-x. 3 0 0 4096 Mar  4 16:19 ..
lrwxrwxrwx. 1 0 0   11 Aug  4  2014 menu.lst -> ./grub.cfg
-rw-r--r--. 1 0 0   64 Sep 18  2015 device.map
-rw-r--r--. 1 0 0 7040 Mar 29 13:30 grub.cfg
"""

LS_BOOT_WITHOUT_KDUMP = """
/boot:
total 187380
dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
dr-xr-xr-x. 19 0 0     4096 Jul 14 09:10 ..
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
drwxr-xr-x.  6 0 0      111 Jun 15 09:51 grub2

/boot/grub2:
total 36
drwxr-xr-x. 6 0 0  104 Mar  4 16:16 .
dr-xr-xr-x. 3 0 0 4096 Mar  4 16:19 ..
lrwxrwxrwx. 1 0 0   11 Aug  4  2014 menu.lst -> ./grub.cfg
-rw-r--r--. 1 0 0   64 Sep 18  2015 device.map
-rw-r--r--. 1 0 0 7040 Mar 29 13:30 grub.cfg
"""


def test_kdump_initramfs_image():
    ls_boot = LsBoot(context_wrap(LS_BOOT_WITH_KDUMP))

    broker = {
        LsBoot: ls_boot
    }
    result = kdump_image(broker)
    assert result is not None
    assert result == ['/boot/initramfs-4.18.0-240.el8.x86_64kdump.img']


def test_without_kdump_initramfs_image():
    ls_boot = LsBoot(context_wrap(LS_BOOT_WITHOUT_KDUMP))

    broker = {
        LsBoot: ls_boot
    }
    with pytest.raises(SkipComponent):
        kdump_image(broker)
