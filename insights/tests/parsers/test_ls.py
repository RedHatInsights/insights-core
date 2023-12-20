from insights.parsers.ls import (
    LSla, LSlaFiltered, LSlan, LSlanFiltered,
    LSlanL, LSlanR, LSlanRL, LSlaRZ, LSlaZ
)
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

LS_LARZ_CONTENT1 = """
/var/log:
total 13500
drwxr-xr-x. 16 root   root   system_u:object_r:var_log_t:s0                    4096 Oct 15 00:00 .
drwxr-xr-x. 20 root   root   system_u:object_r:var_t:s0                        4096 May 27  2022 ..
drwxr-xr-x.  2 root   root   system_u:object_r:var_log_t:s0                    4096 May 27  2022 anaconda
drwx------.  2 root   root   system_u:object_r:auditd_log_t:s0                   99 Oct 16 04:58 audit
-rw-------.  1 root   root   system_u:object_r:plymouthd_var_log_t:s0             0 May 11 00:00 boot.log
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5220 Sep 23 23:44 hawkey.log-20230924
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5160 Sep 30 21:40 hawkey.log-20231001
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5340 Oct  7 23:50 hawkey.log-20231008
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5640 Oct 14 23:26 hawkey.log-20231015
drwx------.  2 root   root   system_u:object_r:insights_client_var_log_t:s0     120 Oct 17 00:17 insights-client
-rw-r--r--.  1 root   root   system_u:object_r:var_log_t:s0                    8062 May 10 09:55 kdump.log -> false-link.log

/var/log/anaconda:
total 5228
drwxr-xr-x.  2 root root system_u:object_r:var_log_t:s0    4096 May 27  2022 .
drwxr-xr-x. 16 root root system_u:object_r:var_log_t:s0    4096 Oct 15 00:00 ..
-rw-------.  1 root root system_u:object_r:var_log_t:s0   46971 May 27  2022 anaconda.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0    3641 May 27  2022 dbus.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0    1799 May 27  2022 dnf.librepo.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0     120 May 27  2022 hawkey.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0 3519082 May 27  2022 journal.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0      40 May 27  2022 ks-script-d2lfa1o_.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0      63 May 27  2022 ks-script-r_i_73z0.log
-rw-------.  1 root root system_u:object_r:var_log_t:s0       0 May 27  2022 ks-script-w3x_f4hl.log
"""

LS_LARZ_CONTENT2 = """
/var/log/rhsm:
drwxr-xr-x. root root system_u:object_r:rhsmcertd_log_t:s0 .
drwxr-xr-x. root root system_u:object_r:var_log_t:s0   ..
-rw-r--r--. root root unconfined_u:object_r:rhsmcertd_log_t:s0 rhsm.log
-rw-r--r--. root root unconfined_u:object_r:rhsmcertd_log_t:s0 rhsm.log-20231015
-rw-r--r--. root root system_u:object_r:rhsmcertd_log_t:s0 rhsmcertd.log
-rw-r--r--. root root system_u:object_r:rhsmcertd_log_t:s0 rhsmcertd.log-20231015

/var/log/sa:
drwxr-xr-x. root root system_u:object_r:sysstat_log_t:s0 .
drwxr-xr-x. root root system_u:object_r:var_log_t:s0   ..
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa12
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa13
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa14
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa15
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa16
-rw-r--r--  root root ?                                sa17
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar12
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar13
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar14
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar15
-rw-r--r--  root root ?                                sar16
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

LS_LAZ_CONTENT1 = """
/var/log:
total 13500
drwxr-xr-x. 16 root   root   system_u:object_r:var_log_t:s0                    4096 Oct 15 00:00 .
drwxr-xr-x. 20 root   root   system_u:object_r:var_t:s0                        4096 May 27  2022 ..
drwxr-xr-x.  2 root   root   system_u:object_r:var_log_t:s0                    4096 May 27  2022 anaconda
drwx------.  2 root   root   system_u:object_r:auditd_log_t:s0                   99 Oct 16 04:58 audit
-rw-------.  1 root   root   system_u:object_r:plymouthd_var_log_t:s0             0 May 11 00:00 boot.log
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5220 Sep 23 23:44 hawkey.log-20230924
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5160 Sep 30 21:40 hawkey.log-20231001
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5340 Oct  7 23:50 hawkey.log-20231008
-rw-r--r--.  1 root   root   unconfined_u:object_r:rpm_log_t:s0                5640 Oct 14 23:26 hawkey.log-20231015
drwx------.  2 root   root   system_u:object_r:insights_client_var_log_t:s0     120 Oct 17 00:17 insights-client
-rw-r--r--.  1 root   root   system_u:object_r:var_log_t:s0                    8062 May 10 09:55 kdump.log
"""

LS_LAZ_CONTENT2 = """
/var/log/rhsm:
drwxr-xr-x. root root system_u:object_r:rhsmcertd_log_t:s0 .
drwxr-xr-x. root root system_u:object_r:var_log_t:s0   ..
-rw-r--r--. root root unconfined_u:object_r:rhsmcertd_log_t:s0 rhsm.log
-rw-r--r--. root root unconfined_u:object_r:rhsmcertd_log_t:s0 rhsm.log-20231015
-rw-r--r--. root root system_u:object_r:rhsmcertd_log_t:s0 rhsmcertd.log
-rw-r--r--. root root system_u:object_r:rhsmcertd_log_t:s0 rhsmcertd.log-20231015

/var/log/sa:
drwxr-xr-x. root root system_u:object_r:sysstat_log_t:s0 .
drwxr-xr-x. root root system_u:object_r:var_log_t:s0   ..
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa12
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa13
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa14
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa15
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sa16
-rw-r--r--  root root ?                                sa17
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar12
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar13
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar14
-rw-r--r--. root root system_u:object_r:sysstat_log_t:s0 sar15
-rw-r--r--  root root ?                                sar16

/dev:
crw-rw----. root root    system_u:object_r:clock_device_t:s0 rtc0
drwxrwxrwt. root root    system_u:object_r:tmpfs_t:s0     shm
crw-rw----. root root    system_u:object_r:apm_bios_t:s0  snapshot
lrwxrwxrwx. root root    system_u:object_r:device_t:s0    stderr -> /proc/self/fd/2
lrwxrwxrwx. root root    system_u:object_r:device_t:s0    stdin -> /proc/self/fd/0
lrwxrwxrwx. root root    system_u:object_r:device_t:s0    stdout -> /proc/self/fd/1
lrwxrwxrwx. root root    system_u:object_r:device_t:s0    systty -> tty0
"""

LS_LAZ_CONTENT3_RHEL8_SELINUX = """
/etc:
total 1352
drwxr-xr-x. 133 root root   system_u:object_r:etc_t:s0                      12288 Nov 12 23:55 .
dr-xr-xr-x.  21 root root   system_u:object_r:root_t:s0                      4096 Jul  5  2022 ..
-rw-r--r--    1 root root   ?                                                1529 Apr 15  2020 aliases
-rw-r--r--    1 root root   ?                                               12288 Jul  5  2022 aliases.db
-rw-r--r--.   1 root root   system_u:object_r:etc_t:s0                          1 Aug 12  2018 at.deny
drwxr-x---.   4 root root   system_u:object_r:auditd_etc_t:s0                 150 Nov 12 23:55 audit
drwxr-xr-x.   2 root root   system_u:object_r:etc_t:s0                        160 Sep 15 12:32 bash_completion.d
-rw-r--r--    1 root root   ?                                                3019 Apr 15  2020 bashrc
-rw-r--r--    1 root root   ?                                                 881 Jul  5  2022 chrony.conf
-rw-r-----.   1 root chrony system_u:object_r:chronyd_keys_t:s0               540 May 10  2019 chrony.keys
drwxr-xr-x.   2 root root   system_u:object_r:etc_t:s0                         26 Jul 28  2021 cifs-utils

/var/log:
total 114496
drwxr-xr-x. 17 root   root   system_u:object_r:var_log_t:s0               8192 Nov 12 03:47 .
drwxr-xr-x. 23 root   root   system_u:object_r:var_t:s0                   4096 Jul  5  2022 ..
drwxr-xr-x   3 root   root   ?                                             122 Jul  5  2022 Automation
drwxr-xr-x.  2 root   root   system_u:object_r:var_log_t:s0                280 Mar 11  2020 anaconda
drwx------.  2 root   root   system_u:object_r:auditd_log_t:s0              99 Nov 12 19:00 audit
-rw-------.  1 root   root   system_u:object_r:plymouthd_var_log_t:s0        0 Jul  5  2022 boot.log
-rw-------   1 root   root   ?                                           79952 Sep 30  2020 boot.log-20200930
-rw-------   1 root   root   ?                                           22027 Jul  5  2022 boot.log-20220705
-rw-------   1 root   utmp   ?                                               0 Nov  1 03:15 btmp
drwxr-xr-x.  2 chrony chrony system_u:object_r:chronyd_var_log_t:s0          6 Mar  1  2021 chrony
""".strip()


LS_LARZ_DEV_CONTENT1 = """
/dev:
total 0
drwxr-xr-x. 19 root root    system_u:object_r:device_t:s0                  3180 May 10 09:54 .
dr-xr-xr-x. 18 root root    system_u:object_r:root_t:s0                     235 May 27  2022 ..
crw-r--r--.  1 root root    system_u:object_r:autofs_device_t:s0        10, 235 May 10 09:54 autofs
drwxr-xr-x.  2 root root    system_u:object_r:device_t:s0                   140 Jun 15 16:11 block
drwxr-xr-x.  3 root root    system_u:object_r:device_t:s0                    60 May 10 09:54 bus
drwxr-xr-x.  2 root root    system_u:object_r:device_t:s0                  2680 May 10 09:55 char
crw--w----.  1 root tty     system_u:object_r:console_device_t:s0        5,   1 May 10 09:54 console

/dev/vfio:
total 0
drwxr-xr-x.  2 root root system_u:object_r:device_t:s0           60 May 10 09:54 .
drwxr-xr-x. 19 root root system_u:object_r:device_t:s0         3180 May 10 09:54 ..
crw-rw-rw-.  1 root root system_u:object_r:vfio_device_t:s0 10, 196 May 10 09:54 vfio -> false_link_2
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

    assert ls.files_of('non-exist') == []
    assert ls.dirs_of('non-exist') == []
    assert ls.specials_of('non-exist') == []
    assert ls.listing_of('non-exist') == []
    assert ls.total_of('non-exist') == 0
    assert ls.dir_contains('non-exist', 'test') is False
    assert ls.dir_entry('non-exist', 'test') == {}


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


def test_ls_laRZ():
    ls = LSlaRZ(context_wrap(LS_LARZ_CONTENT1))
    assert '/var/log' in ls
    assert '/var/log/anaconda' in ls
    assert '/var/log/atest' not in ls
    assert ls.dirs_of('/var/log') == ['.', '..', 'anaconda', 'audit', 'insights-client']

    dev_listings = ls.listing_of('/var/log')
    assert 'boot.log' in dev_listings
    assert dev_listings["boot.log"]['se_type'] == 'plymouthd_var_log_t'
    assert 'kdump.log' in dev_listings
    assert dev_listings["kdump.log"]['link'] == 'false-link.log'

    ls = LSlaRZ(context_wrap(LS_LARZ_CONTENT2))
    assert '/var/log/rhsm' in ls

    dev_listings = ls.listing_of('/var/log/rhsm')
    assert "rhsm.log" in dev_listings
    assert 'se_type' in dev_listings["rhsm.log"]
    assert dev_listings["rhsm.log"]['se_type'] == 'rhsmcertd_log_t'


def test_ls_laZ():
    ls = LSlaZ(context_wrap(LS_LAZ_CONTENT1))
    assert '/var/log/anaconda' not in ls

    dev_listings = ls.listing_of('/var/log')
    assert "hawkey.log-20230924" in dev_listings
    assert dev_listings["hawkey.log-20230924"]['se_type'] == 'rpm_log_t'
    assert dev_listings["hawkey.log-20230924"]['size'] == 5220

    ls = LSlaZ(context_wrap(LS_LAZ_CONTENT2))
    assert '/var/log/rhsm' in ls

    dev_listings = ls.listing_of('/var/log/rhsm')
    assert "rhsm.log" in dev_listings
    assert 'se_type' in dev_listings["rhsm.log"]
    assert dev_listings["rhsm.log"]['se_type'] == 'rhsmcertd_log_t'

    dev_listings = ls.listing_of('/dev')
    assert 'stderr' in dev_listings
    assert dev_listings["stderr"]['link'] == '/proc/self/fd/2'

    ls = LSlaZ(context_wrap(LS_LAZ_CONTENT3_RHEL8_SELINUX))
    assert '/etc' in ls

    dev_listings = ls.listing_of('/etc')
    assert "bashrc" in dev_listings
    assert dev_listings["bashrc"]['se_user'] == '?'
    assert dev_listings["bashrc"]['se_role'] is None
    assert dev_listings["bashrc"]['se_type'] is None
    assert "chrony.conf" in dev_listings
    assert 'se_type' in dev_listings["chrony.conf"]
    assert dev_listings["chrony.keys"]['se_type'] == 'chronyd_keys_t'

    dev_listings = ls.listing_of('/var/log')
    assert 'boot.log-20220705' in dev_listings
    assert dev_listings["boot.log-20220705"]['size'] == 22027


def test_ls_laZ_on_dev():
    ls = LSlaRZ(context_wrap(LS_LARZ_DEV_CONTENT1))
    assert '/dev' in ls
    dev_listings = ls.listing_of('/dev')
    assert "autofs" in dev_listings
    assert 'se_type' in dev_listings["autofs"]
    assert dev_listings["autofs"]['se_type'] == 'autofs_device_t'
    assert dev_listings["autofs"]['major'] == 10
    assert dev_listings["autofs"]['minor'] == 235
    assert "block" in dev_listings
    assert dev_listings['block']['size'] == 140

    dev_listings = ls.listing_of('/dev/vfio')
    assert 'vfio' in dev_listings
    assert dev_listings["vfio"]['link'] == 'false_link_2'
