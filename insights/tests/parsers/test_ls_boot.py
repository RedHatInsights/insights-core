import doctest

from insights.parsers import ls_boot
from insights.parsers.ls_boot import LsBoot
from insights.tests import context_wrap

LS_LANR_BOOT = """
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

LS_ALZR_BOOT = """
/boot:
total 187380
dr-xr-xr-x.  3 root root system_u:object_r:boot_t:s0   4096 Oct  4  2023 .
dr-xr-xr-x. 19 root root system_u:object_r:boot_t:s0   4096 Apr 21  2023 ..
-rw-r--r--.  1 root root system_u:object_r:boot_t:s0 123891 Sep 30  2022 config-5.14.0-162.6.1.el9_1.aarch64
drwxr-xr-x.  6 root root system_u:object_r:boot_t:s0    111 Aug 28 16:42 grub2

/boot/grub2:
total 16
drwx------. 3 root root system_u:object_r:boot_t:s0       50 Aug 28 16:42 .
dr-xr-xr-x. 6 root root system_u:object_r:boot_t:s0     4096 Oct  4  2023 ..
drwx------. 2 root root system_u:object_r:boot_t:s0       25 Apr 21  2023 fonts
-rwx------. 1 root root system_u:object_r:boot_t:s0     6535 Apr 21  2023 grub.cfg
-rw-------. 1 root root unconfined_u:object_r:boot_t:s0 1024 Aug 28 16:42 grubenv
"""

LS_LANR_BOOT_LINKS = """
/boot:
total 187380
-rw-------.  1 root root 19143244 Mar  3 14:31 initramfs-2.6.32-504.el6.x86_64.img
lrwxrwxrwx.  1 root root       40 May 11 11:00 initrd -> initramfs-2.6.32-504.12.2.el6.x86_64.img
lrwxrwxrwx.  1 root root       34 May 11 11:00 vmlinuz -> vmlinuz-2.6.32-504.12.2.el6.x86_64
-rwxr-xr-x.  1 root root  4153904 Sep 16  2014 vmlinuz-2.6.32-504.el6.x86_64
"""

LS_ALZR_BOOT_LINKS = """
/boot:
total 187380
lrwxrwxrwx.  1 root root system_u:object_r:boot_t:s0              32 Apr 21  2023 dtb -> dtb-5.14.0-162.6.1.el9_1.aarch64
drwxr-xr-x. 11 root root system_u:object_r:boot_t:s0             129 Apr 21  2023 dtb-5.14.0-162.6.1.el9_1.aarch64
-rw-------.  1 root root system_u:object_r:boot_t:s0       103122590 Apr 21  2023 initramfs-0-rescue-6c7d8d74767a419884156df2b0005e3e.img
-rw-------.  1 root root system_u:object_r:boot_t:s0        54790153 Apr 21  2023 initramfs-5.14.0-162.6.1.el9_1.aarch64.img
-rw-------.  1 root root system_u:object_r:boot_t:s0        32324096 Oct  4  2023 initramfs-5.14.0-162.6.1.el9_1.aarch64kdump.img
drwxr-xr-x.  3 root root system_u:object_r:boot_t:s0              21 Apr 21  2023 loader
lrwxrwxrwx.  1 root root system_u:object_r:boot_t:s0              52 Apr 21  2023 symvers-5.14.0-162.6.1.el9_1.aarch64.gz -> /lib/modules/5.14.0-162.6.1.el9_1.aarch64/symvers.gz
"""


def test_ls_boot():
    ls_boot = LsBoot(context_wrap(LS_LANR_BOOT))
    assert "/boot" in ls_boot
    assert "/boot/grub2" in ls_boot
    assert ls_boot.dirs_of("/boot") == [".", "..", "grub2"]

    grub2_files = ls_boot.files_of("/boot/grub2")
    assert "menu.lst" in grub2_files
    assert "device.map" in grub2_files
    assert "grub.cfg" in grub2_files
    assert len(grub2_files) == 3

    boot_files = ls_boot.files_of("/boot")
    assert "config-3.10.0-229.14.1.el7.x86_64" in boot_files
    assert len(boot_files) == 1

    ls_alzr_boot = LsBoot(context_wrap(LS_ALZR_BOOT))
    assert "/boot" in ls_alzr_boot
    assert ls_alzr_boot.files_of("/boot") == ["config-5.14.0-162.6.1.el9_1.aarch64"]
    assert ls_alzr_boot.dirs_of("/boot") == [".", "..", "grub2"]
    assert ls_alzr_boot.get("/boot/grub2")["entries"].get("grub.cfg") == {
        "type": "-",
        "perms": "rwx------.",
        "links": 1,
        "owner": "root",
        "group": "root",
        "size": 6535,
        "se_user": "system_u",
        "se_role": "object_r",
        "se_type": "boot_t",
        "se_mls": "s0",
        "name": "grub.cfg",
        "date": "Apr 21  2023",
        "dir": "/boot/grub2",
    }
    assert (
        ls_alzr_boot.raw_entry_of("/boot/grub2", "grub.cfg")
        == "-rwx------. 1 root root system_u:object_r:boot_t:s0 6535 Apr 21  2023 grub.cfg"
    )


def test_boot_links():
    ls_boot = LsBoot(context_wrap(LS_LANR_BOOT_LINKS))
    boot_files = ls_boot.files_of("/boot")
    assert "/boot" in ls_boot
    assert "initramfs-2.6.32-504.el6.x86_64.img" in boot_files
    assert "initrd" in boot_files
    assert "vmlinuz" in boot_files
    assert "vmlinuz-2.6.32-504.el6.x86_64" in boot_files

    ls_alzr_boot = LsBoot(context_wrap(LS_ALZR_BOOT_LINKS))
    assert ls_alzr_boot.total_of("/boot") == 187380
    assert ls_alzr_boot.get("/boot")["entries"].get("dtb") == {
        "type": "l",
        "perms": "rwxrwxrwx.",
        "links": 1,
        "owner": "root",
        "group": "root",
        "size": 32,
        "se_user": "system_u",
        "se_role": "object_r",
        "se_type": "boot_t",
        "se_mls": "s0",
        "name": "dtb",
        "date": "Apr 21  2023",
        "link": "dtb-5.14.0-162.6.1.el9_1.aarch64",
        "dir": "/boot",
    }
    assert (
        ls_alzr_boot.raw_entry_of("/boot", "dtb")
        == "lrwxrwxrwx. 1 root root system_u:object_r:boot_t:s0 32 Apr 21  2023 dtb -> dtb-5.14.0-162.6.1.el9_1.aarch64"
    )


def test_doc_examples():
    env = {"bootdir": LsBoot(context_wrap(LS_LANR_BOOT))}
    failed, total = doctest.testmod(ls_boot, globs=env)
    assert failed == 0
