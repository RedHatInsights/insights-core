import pytest

from mock.mock import Mock

from insights.core.exceptions import SkipComponent
from insights.specs.datasources.mdadm import LocalSpecs, raid_devices


LS_DEV_MD_1 = """
/dev/md1  /dev/md2  /dev/md3
""".strip()

LS_DEV_MD_2 = """
/dev/md1   /dev/md14  /dev/md20  /dev/md27  /dev/md33  /dev/md4   /dev/md46  /dev/md52  /dev/md59  /dev/md8
/dev/md0   /dev/md15  /dev/md21  /dev/md28  /dev/md34  /dev/md40  /dev/md47  /dev/md53  /dev/md6   /dev/md9
""".strip()

LS_DEV_MD_3 = """
ls: cannot access '/dev/md*': No such file or directory
""".strip()


def test_raid_devices():
    ls_dev_md_command = Mock()
    ls_dev_md_command.content = LS_DEV_MD_1.splitlines()
    broker = {LocalSpecs.ls_dev_md: ls_dev_md_command}
    result = raid_devices(broker)
    assert result is not None
    assert isinstance(result, str)
    assert result == "/dev/md1 /dev/md2 /dev/md3"


def test_raid_devices_bad():
    ls_dev_md_command = Mock()
    ls_dev_md_command.content = LS_DEV_MD_3.splitlines()
    broker = {LocalSpecs.ls_dev_md: ls_dev_md_command}
    with pytest.raises(SkipComponent):
        raid_devices(broker)

    ls_dev_md_command = Mock()
    ls_dev_md_command.content = ""
    broker = {LocalSpecs.ls_dev_md: ls_dev_md_command}
    with pytest.raises(SkipComponent):
        raid_devices(broker)
