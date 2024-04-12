import doctest
import pytest

from insights.core.dr import SkipComponent
from insights.parsers import file
from insights.parsers.file import BootLoaderOnDisk
from insights.tests import context_wrap

BOOT_LOADER_1 = """
/dev/vda: x86 boot sector; partition 1: ID=0x83, active, starthead 0, startsector 2048, 167770079 sectors, code offset 0x63
""".strip()

BOOT_LOADER_2 = """
/vda: x86 boot sector; partition 1: ID=0x83, active, starthead 0, startsector 2048, 167770079 sectors, code offset 0x63
""".strip()

BOOT_LOADER_3 = """
invalid line 1
invalid line 2
""".strip()

BOOT_LOADER_4 = """
/dev/vda
""".strip()


def test_boot_loader_on_disk():
    boot_loader_on_disk = BootLoaderOnDisk(context_wrap(BOOT_LOADER_1))
    assert boot_loader_on_disk.boot_device == "/dev/vda"
    expected = "x86 boot sector; partition 1: ID=0x83, active, starthead 0, startsector 2048, 167770079 sectors, code offset 0x63"
    assert boot_loader_on_disk.boot_loader == expected

    with pytest.raises(SkipComponent) as e_info:
        BootLoaderOnDisk(context_wrap(BOOT_LOADER_2))
    assert "Content doesn't contain a valid device." in str(e_info.value)

    with pytest.raises(SkipComponent) as e_info:
        BootLoaderOnDisk(context_wrap(BOOT_LOADER_3))
    assert "Command output should only contain one line." in str(e_info.value)

    with pytest.raises(SkipComponent) as e_info:
        BootLoaderOnDisk(context_wrap(BOOT_LOADER_4))
    assert "Content format is invalid." in str(e_info.value)


def test_doc_examples():
    env = {
            'boot_loader_on_disk':
            BootLoaderOnDisk(context_wrap(BOOT_LOADER_1)),
          }
    failed, total = doctest.testmod(file, globs=env)
    assert failed == 0
