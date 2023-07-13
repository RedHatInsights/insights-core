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


def test_ls_sys_firmware():
    ls = LsSysFirmware(context_wrap(LS_SYS_FIRMWARE))
    assert "acpi" not in ls
    assert "/sys/firmware/acpi" in ls
    assert ls.dirs_of("/sys/firmware") == ['.', '..', 'acpi', 'dmi', 'memmap']
    assert ls.files_of("/sys/firmware/acpi") == ['pm_profile']


def test_doc_examples():
    env = {'ls_sys_firmware': LsSysFirmware(context_wrap(LS_SYS_FIRMWARE))}
    failed, total = doctest.testmod(ls_sys_firmware, globs=env)
    assert failed == 0
