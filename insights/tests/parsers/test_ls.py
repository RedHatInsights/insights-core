from insights.parsers.ls import (LSla, LSlaFiltered, LSlan, LSlanFiltered,
                                 LSlanL, LSlanR, LSlanRL, LSlanRZ, LSlanZ)
from insights.tests import context_wrap

LS_LA = """
ls: cannot access '_non_existing_': No such file or directory
/boot:
total 187380
dr-xr-xr-x.  3 root root     4096 Mar  4 16:19 .
dr-xr-xr-x. 19 root root     4096 Jul 14 09:10 ..
-rw-r--r--.  1 root root   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
drwxr-xr-x.  6 root root      111 Jun 15 09:51 grub2

/boot/grub2:
total 36
drwxr-xr-x. 6 root root  104 Mar  4 16:16 .
dr-xr-xr-x. 3 root root 4096 Mar  4 16:19 ..
lrwxrwxrwx. 1 root root   11 Aug  4  2014 menu.lst -> ./grub.cfg
-rw-r--r--. 1 root root   64 Sep 18  2015 device.map
-rw-r--r--. 1 root root 7040 Mar 29 13:30 grub.cfg
"""

LS_LAN = """
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


LS_LANL = """
ls: cannot access '_non_existing_': No such file or directory
/boot:
total 187380
dr-xr-xr-x.  3 0 0     4096 Mar  4 16:19 .
dr-xr-xr-x. 19 0 0     4096 Jul 14 09:10 ..
-rw-r--r--.  1 0 0   123891 Aug 25  2015 config-3.10.0-229.14.1.el7.x86_64
drwxr-xr-x.  6 0 0      111 Jun 15 09:51 grub2

/boot/grub2:
total 32
drwx------. 4 0 0   83 Jun 27 11:01 .
dr-xr-xr-x. 5 0 0 4096 Jun  5 09:14 ..
-rw-r--r--. 1 0 0   11 Aug  4  2014 menu.lst
-rw-r--r--. 1 0 0   64 Jan 17 16:10 device.map
-rw-------. 1 0 0 6529 Jan 17 16:10 grub.cfg
"""

LS_LANR = """
ls: cannot access '_non_existing_': No such file or directory
/dev:
total 0
drwxr-xr-x. 21 0  0     3100 Jun 27 10:58 .
dr-xr-xr-x. 17 0  0      224 Apr 17 16:45 ..
crw-r--r--.  1 0  0  10, 235 Jun 27 10:58 autofs
drwxr-xr-x.  2 0  0      160 Jun 27 10:58 block
lrwxrwxrwx.  1 0  0        3 Jun 27 10:58 cdrom -> sr0

/dev/vfio:
total 0
drwxr-xr-x.  2 0 0      60 Jun 27 10:58 .
drwxr-xr-x. 21 0 0    3100 Jun 27 10:58 ..
crw-------.  1 0 0 10, 196 Jun 27 10:58 vfio

/dev/virtio-ports:
total 0
drwxr-xr-x.  2 0 0   80 Jun 27 10:58 .
drwxr-xr-x. 21 0 0 3100 Jun 27 10:58 ..
lrwxrwxrwx.  1 0 0   11 Jun 27 10:58 com.redhat.spice.0 -> ../vport2p2
lrwxrwxrwx.  1 0 0   11 Jun 27 10:58 org.qemu.guest_agent.0 -> ../vport2p1
"""

LS_LANRL = """
/dev:
total 0
drwxr-xr-x. 21    0  0            3100 Jun 27 10:58 .
dr-xr-xr-x. 17    0  0             224 Apr 17 16:45 ..
crw-r--r--.  1    0  0         10, 235 Jun 27 10:58 autofs
drwxr-xr-x.  2    0  0             160 Jun 27 10:58 block
brw-rw----.  1    0 11         11,   0 Jun 27 10:58 cdrom

/dev/vfio:
total 0
drwxr-xr-x.  2 0 0      60 Jun 27 10:58 .
drwxr-xr-x. 21 0 0    3100 Jun 27 10:58 ..
crw-------.  1 0 0 10, 196 Jun 27 10:58 vfio

/dev/virtio-ports:
total 0
drwxr-xr-x.  2 0 0     80 Jun 27 10:58 .
drwxr-xr-x. 21 0 0   3100 Jun 27 10:58 ..
crw-------.  1 0 0 243, 2 Jun 27 10:58 com.redhat.spice.0
crw-------.  1 0 0 243, 1 Jun 27 10:58 org.qemu.guest_agent.0
"""

LS_LANRZ = """
/dev:
total 0
drwxr-xr-x. 21 0  0 system_u:object_r:device_t:s0                  3100 Jun 27 10:58 .
dr-xr-xr-x. 17 0  0 system_u:object_r:root_t:s0                     224 Apr 17 16:45 ..
crw-r--r--.  1 0  0 system_u:object_r:autofs_device_t:s0            235 Jun 27 10:58 autofs
drwxr-xr-x.  2 0  0 system_u:object_r:device_t:s0                   160 Jun 27 10:58 block
lrwxrwxrwx.  1 0  0 system_u:object_r:device_t:s0                     3 Jun 27 10:58 cdrom -> sr0

/dev/vfio:
total 0
drwxr-xr-x.  2 0 0 system_u:object_r:device_t:s0           60 Jun 27 10:58 .
drwxr-xr-x. 21 0 0 system_u:object_r:device_t:s0         3100 Jun 27 10:58 ..
crw-------.  1 0 0 system_u:object_r:vfio_device_t:s0     196 Jun 27 10:58 vfio

/dev/virtio-ports:
total 0
drwxr-xr-x.  2 0 0 system_u:object_r:device_t:s0   80 Jun 27 10:58 .
drwxr-xr-x. 21 0 0 system_u:object_r:device_t:s0 3100 Jun 27 10:58 ..
lrwxrwxrwx.  1 0 0 system_u:object_r:device_t:s0   11 Jun 27 10:58 com.redhat.spice.0 -> ../vport2p2
lrwxrwxrwx.  1 0 0 system_u:object_r:device_t:s0   11 Jun 27 10:58 org.qemu.guest_agent.0 -> ../vport2p1
"""

LS_LANZ = """
/dev:
total 0
drwxr-xr-x. 21 0  0 system_u:object_r:device_t:s0          3100 Jun 27 10:58 .
dr-xr-xr-x. 17 0  0 system_u:object_r:root_t:s0             224 Apr 17 16:45 ..
crw-r--r--.  1 0  0 system_u:object_r:autofs_device_t:s0    235 Jun 27 10:58 autofs
drwxr-xr-x.  2 0  0 system_u:object_r:device_t:s0           160 Jun 27 10:58 block
lrwxrwxrwx.  1 0  0 system_u:object_r:device_t:s0             3 Jun 27 10:58 cdrom -> sr0
"""


def test_ls_la():
    ls = LSla(context_wrap(LS_LA))
    assert '/boot' in ls
    assert '/boot/grub2' in ls
    assert ls.dirs_of('/boot') == ['.', '..', 'grub2']

    grub2_files = ls.files_of('/boot/grub2')
    assert 'menu.lst' in grub2_files
    assert 'device.map' in grub2_files
    assert 'grub.cfg' in grub2_files
    assert len(grub2_files) == 3

    boot_files = ls.files_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_files
    assert len(boot_files) == 1

    boot_listings = ls.listing_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_listings
    assert boot_listings["config-3.10.0-229.14.1.el7.x86_64"]['owner'] == 'root'

    grub_listings = ls.listing_of('/boot/grub2')
    assert "menu.lst" in grub_listings
    assert grub_listings["menu.lst"]['group'] == 'root'
    assert 'link' in grub_listings["menu.lst"]
    assert grub_listings["menu.lst"]['link'] == './grub.cfg'


def test_ls_la_filtered():
    ls = LSlaFiltered(context_wrap(LS_LA))
    assert '/boot' in ls
    assert '/boot/grub2' in ls
    assert ls.dirs_of('/boot') == ['.', '..', 'grub2']

    grub2_files = ls.files_of('/boot/grub2')
    assert 'menu.lst' in grub2_files
    assert 'device.map' in grub2_files
    assert 'grub.cfg' in grub2_files
    assert len(grub2_files) == 3

    boot_files = ls.files_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_files
    assert len(boot_files) == 1

    boot_listings = ls.listing_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_listings
    assert boot_listings["config-3.10.0-229.14.1.el7.x86_64"]['owner'] == 'root'

    grub_listings = ls.listing_of('/boot/grub2')
    assert "menu.lst" in grub_listings
    assert grub_listings["menu.lst"]['group'] == 'root'
    assert 'link' in grub_listings["menu.lst"]
    assert grub_listings["menu.lst"]['link'] == './grub.cfg'


def test_ls_lan():
    ls = LSlan(context_wrap(LS_LAN))
    assert '/boot' in ls
    assert '/boot/grub2' in ls
    assert ls.dirs_of('/boot') == ['.', '..', 'grub2']

    grub2_files = ls.files_of('/boot/grub2')
    assert 'menu.lst' in grub2_files
    assert 'device.map' in grub2_files
    assert 'grub.cfg' in grub2_files
    assert len(grub2_files) == 3

    boot_files = ls.files_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_files
    assert len(boot_files) == 1

    boot_listings = ls.listing_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_listings
    assert boot_listings["config-3.10.0-229.14.1.el7.x86_64"]['owner'] == '0'

    grub_listings = ls.listing_of('/boot/grub2')
    assert "menu.lst" in grub_listings
    assert grub_listings["menu.lst"]['group'] == '0'
    assert 'link' in grub_listings["menu.lst"]
    assert grub_listings["menu.lst"]['link'] == './grub.cfg'


def test_ls_lan_filtered():
    ls = LSlanFiltered(context_wrap(LS_LAN))
    assert '/boot' in ls
    assert '/boot/grub2' in ls
    assert ls.dirs_of('/boot') == ['.', '..', 'grub2']

    grub2_files = ls.files_of('/boot/grub2')
    assert 'menu.lst' in grub2_files
    assert 'device.map' in grub2_files
    assert 'grub.cfg' in grub2_files
    assert len(grub2_files) == 3

    boot_files = ls.files_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_files
    assert len(boot_files) == 1

    boot_listings = ls.listing_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_listings
    assert boot_listings["config-3.10.0-229.14.1.el7.x86_64"]['owner'] == '0'

    grub_listings = ls.listing_of('/boot/grub2')
    assert "menu.lst" in grub_listings
    assert grub_listings["menu.lst"]['group'] == '0'
    assert 'link' in grub_listings["menu.lst"]
    assert grub_listings["menu.lst"]['link'] == './grub.cfg'


def test_ls_lanL():
    ls = LSlanL(context_wrap(LS_LANL))
    assert '/boot' in ls
    assert '/boot/grub2' in ls
    assert ls.dirs_of('/boot') == ['.', '..', 'grub2']

    grub2_files = ls.files_of('/boot/grub2')
    assert 'menu.lst' in grub2_files
    assert 'device.map' in grub2_files
    assert 'grub.cfg' in grub2_files
    assert len(grub2_files) == 3

    boot_files = ls.files_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_files
    assert len(boot_files) == 1

    boot_listings = ls.listing_of('/boot')
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_listings
    assert boot_listings["config-3.10.0-229.14.1.el7.x86_64"]['owner'] == '0'

    grub_listings = ls.listing_of('/boot/grub2')
    assert "menu.lst" in grub_listings
    assert grub_listings["menu.lst"]['group'] == '0'
    assert 'link' not in grub_listings["menu.lst"]


def test_ls_lanR():
    ls = LSlanR(context_wrap(LS_LANR))
    assert '/dev' in ls
    assert '/dev/vfio' in ls
    assert '/dev/virtio-ports' in ls
    assert ls.dirs_of('/dev') == ['.', '..', 'block']

    dev_listings = ls.listing_of('/dev')
    assert "cdrom" in dev_listings
    assert 'link' in dev_listings["cdrom"]
    assert dev_listings["cdrom"]['link'] == 'sr0'

    assert 'link' in ls.listing_of('/dev/virtio-ports')['com.redhat.spice.0']


def test_ls_lanRL():
    ls = LSlanRL(context_wrap(LS_LANRL))
    assert '/dev' in ls
    assert '/dev/vfio' in ls
    assert '/dev/virtio-ports' in ls
    assert ls.dirs_of('/dev') == ['.', '..', 'block']

    dev_listings = ls.listing_of('/dev')
    assert "cdrom" in dev_listings
    assert 'link' not in dev_listings["cdrom"]

    assert 'link' not in ls.listing_of('/dev/virtio-ports')['com.redhat.spice.0']


def test_ls_lanRZ():
    ls = LSlanRZ(context_wrap(LS_LANRZ))
    assert '/dev' in ls
    assert '/dev/vfio' in ls
    assert '/dev/virtio-ports' in ls
    assert ls.dirs_of('/dev') == ['.', '..', 'block']

    dev_listings = ls.listing_of('/dev')
    assert "cdrom" in dev_listings
    assert 'link' in dev_listings["cdrom"]
    assert dev_listings["cdrom"]['link'] == 'sr0'
    assert 'se_type' in dev_listings["cdrom"]
    assert dev_listings["cdrom"]['se_type'] == 'device_t'

    assert 'link' in ls.listing_of('/dev/virtio-ports')['com.redhat.spice.0']


def test_ls_lanZ():
    ls = LSlanZ(context_wrap(LS_LANZ))
    assert '/dev' in ls
    assert '/dev/vfio' not in ls
    assert '/dev/virtio-ports' not in ls
    assert ls.dirs_of('/dev') == ['.', '..', 'block']

    dev_listings = ls.listing_of('/dev')
    assert "cdrom" in dev_listings
    assert 'link' in dev_listings["cdrom"]
    assert dev_listings["cdrom"]['link'] == 'sr0'
    assert 'se_type' in dev_listings["cdrom"]
    assert dev_listings["cdrom"]['se_type'] == 'device_t'
