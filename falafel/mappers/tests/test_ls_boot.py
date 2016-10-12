from falafel.mappers.ls_boot import LsBoot
from falafel.tests import context_wrap

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
lrwxrwxrwx. 1 0 0     11 Aug  4  2014 menu.lst -> ./grub.conf
-rw-r--r--. 1 0 0   64 Sep 18  2015 device.map
"""


def test_ls_boot():
    ls_boot = LsBoot(context_wrap(LS_BOOT))
    assert ls_boot.data[0] == "config-3.10.0-229.14.1.el7.x86_64"
    assert ls_boot.data[1] == "menu.lst"
    assert len(ls_boot.data) == 3
