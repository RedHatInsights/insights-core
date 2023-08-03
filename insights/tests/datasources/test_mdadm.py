import pytest

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.mdadm import md_raid_arrays
from insights.parsers.mdstat import Mdstat
from insights.tests import context_wrap

MDSTAT_TEST_2 = """
Personalities : [raid1] [raid6] [raid5] [raid4]
md1 : active raid1 sdb2[1] sda2[0]
      136448 blocks [2/2] [UU]

md2 : active raid1 sdb3[1] sda3[0]
      129596288 blocks [2/2] [U_]

md0 : active raid1 sdb1[1](F) sda1[0]
      16787776 blocks [2/2] [_U]

unused devices: <none>
""".strip()

MDSTAT_TEST_3 = """
Personalities : [linear] [raid0] [raid1]
unused devices: <none>
""".strip()


def test_md_raid_arrays():
    broker = {
        Mdstat: Mdstat(context_wrap(MDSTAT_TEST_2))
    }
    result = md_raid_arrays(broker)
    assert result is not None
    assert result == ["md0", "md1", "md2"]


def test_md_raid_arrays_with_no_device():
    with pytest.raises(SkipComponent):
        md_raid_arrays({Mdstat: Mdstat(context_wrap(MDSTAT_TEST_3))})
