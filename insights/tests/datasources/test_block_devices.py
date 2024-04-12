import pytest

from insights.core.dr import SkipComponent
from insights.parsers.lsblk import LSBlock
from insights.specs.datasources.block_devices import boot_device
from insights.tests import context_wrap

LSBLK_1 = """
NAME          MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
vda           252:0    0    9G  0 disk
|-vda1        252:1    0  500M  0 part /boot
`-vda2        252:2    0  8.5G  0 part
  |-rhel-root 253:0    0  7.6G  0 lvm  /
  |-rhel-swap 253:1    0  924M  0 lvm  [SWAP]
sda             8:0    0  500G  0 disk
`-sda1          8:1    0  500G  0 part /data
""".strip()

LSBLK_2 = """
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda      8:0    0   128G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /data
`-sda4   8:4    0 127.5G  0 part /
""".strip()

LSBLK_3 = """
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINTS
sda      8:0    0   128G  0 disk
|-sda1   8:1    0     1M  0 part
|-sda2   8:2    0   127M  0 part
|-sda3   8:3    0   384M  0 part /data
`-sda4   8:4    0 127.5G  0 part /tmp
""".strip()


def test_boot_device():
    broker = {LSBlock: LSBlock(context_wrap(LSBLK_1))}
    result = boot_device(broker)
    assert result is not None
    assert result == "/dev/vda"

    broker = {LSBlock: LSBlock(context_wrap(LSBLK_2))}
    result = boot_device(broker)
    assert result is not None
    assert result == "/dev/sda"

    broker = {LSBlock: LSBlock(context_wrap(LSBLK_3))}
    with pytest.raises(SkipComponent):
        boot_device(broker)
