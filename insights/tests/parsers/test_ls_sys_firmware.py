import doctest

from insights.parsers import ls_sys_firmware
from insights.parsers.ls_sys_firmware import LsSysFirmware
from insights.tests import context_wrap


LS_SYS_FIRMWARE = """
/sys/firmware:
total 0
drwxr-xr-x.  5 0 0 0 Dec 22 17:56 .
dr-xr-xr-x. 13 0 0 0 Dec 22 17:56 ..
drwxr-xr-x.  5 0 0 0 Dec 22 17:56 acpi
drwxr-xr-x.  3 0 0 0 Dec 22 17:57 dmi
drwxr-xr-x. 10 0 0 0 Dec 22 17:57 memmap

/sys/firmware/acpi:
total 0
drwxr-xr-x. 5 0 0    0 Dec 22 17:56 .
drwxr-xr-x. 5 0 0    0 Dec 22 17:56 ..
drwxr-xr-x. 6 0 0    0 Feb 10 15:54 hotplug
drwxr-xr-x. 2 0 0    0 Feb 10 15:54 interrupts
-r--r--r--. 1 0 0 4096 Feb 10 15:54 pm_profile
drwxr-xr-x. 3 0 0    0 Dec 22 17:56 tables
"""

LS_ALZR_SYS_FIRMWARE = """
/sys/firmware:
total 0
drwxr-xr-x.  7 root root system_u:object_r:sysfs_t:s0   0 Sep 30 16:58 .
dr-xr-xr-x. 12 root root system_u:object_r:sysfs_t:s0   0 Sep 30 16:58 ..
drwxr-xr-x.  5 root root system_u:object_r:sysfs_t:s0   0 Sep 30 16:58 acpi
drwxr-xr-x.  2 root root system_u:object_r:sysfs_t:s0   0 Sep 30 16:58 devicetree
drwxr-xr-x.  4 root root system_u:object_r:sysfs_t:s0   0 Sep 30 16:58 dmi
drwxr-xr-x.  3 root root system_u:object_r:sysfs_t:s0   0 Sep 30 16:58 efi
-r--------.  1 root root system_u:object_r:sysfs_t:s0 657 Oct  1 10:17 fdt

/sys/firmware/acpi:
total 0
drwxr-xr-x. 5 root root system_u:object_r:sysfs_t:s0    0 Sep 30 16:58 .
drwxr-xr-x. 7 root root system_u:object_r:sysfs_t:s0    0 Sep 30 16:58 ..
drwxr-xr-x. 2 root root system_u:object_r:sysfs_t:s0    0 Oct  1 10:17 bgrt
drwxr-xr-x. 5 root root system_u:object_r:sysfs_t:s0    0 Oct  1 10:17 hotplug
-r--r--r--. 1 root root system_u:object_r:sysfs_t:s0 4096 Oct  1 10:17 pm_profile
drwxr-xr-x. 4 root root system_u:object_r:sysfs_t:s0    0 Sep 30 16:58 tables
"""


def test_ls_sys_firmware():
    ls = LsSysFirmware(context_wrap(LS_SYS_FIRMWARE))
    assert "acpi" not in ls
    assert "/sys/firmware/acpi" in ls
    assert ls.dirs_of("/sys/firmware") == [".", "..", "acpi", "dmi", "memmap"]
    assert ls.files_of("/sys/firmware/acpi") == ["pm_profile"]

    ls_alzr_sys_firmware = LsSysFirmware(context_wrap(LS_ALZR_SYS_FIRMWARE))
    assert "/sys/firmware/acpi" in ls_alzr_sys_firmware
    assert "/sys/firmware/dmi" not in ls_alzr_sys_firmware
    assert ls_alzr_sys_firmware.get("/sys/firmware")["entries"].get("efi") == {
        "type": "d",
        "perms": "rwxr-xr-x.",
        "links": 3,
        "owner": "root",
        "group": "root",
        "size": 0,
        "se_user": "system_u",
        "se_role": "object_r",
        "se_type": "sysfs_t",
        "se_mls": "s0",
        "name": "efi",
        "date": "Sep 30 16:58",
        "dir": "/sys/firmware",
    }
    assert (
        ls_alzr_sys_firmware.raw_entry_of("/sys/firmware", "efi")
        == "drwxr-xr-x. 3 root root system_u:object_r:sysfs_t:s0 0 Sep 30 16:58 efi"
    )


def test_doc_examples():
    env = {"ls_sys_firmware": LsSysFirmware(context_wrap(LS_SYS_FIRMWARE))}
    failed, total = doctest.testmod(ls_sys_firmware, globs=env)
    assert failed == 0
