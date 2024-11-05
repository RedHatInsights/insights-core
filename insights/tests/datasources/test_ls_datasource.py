import pytest

from mock.mock import Mock
from insights.core.exceptions import SkipComponent
from insights.specs.datasources.ls_datasource import fstab_mounted, list_with_lad_specific_file
from insights.parsers.fstab import FSTab
from insights.tests import context_wrap
from insights.core import dr
from insights.specs import Specs
from insights.core import filters

FSTAB = """
#
# /etc/fstab
# Created by anaconda on Fri May  6 19:51:54 2016
#
/dev/mapper/rhel_hadoop--test--1-root /                       xfs     defaults        0 0
UUID=2c839365-37c7-4bd5-ac47-040fba761735 /boot               xfs     defaults        0 0
/dev/mapper/rhel_hadoop--test--1-home /home                   xfs     defaults        0 0
/dev/mapper/rhel_hadoop--test--1-swap swap                    swap    defaults        0 0
""".strip()

FSTAB_EMPTY = ""

FSTAB_MOUNTED_CONTEXT = '/ /boot /home swap'


def setup_function(func):
    if func is test_lad_specific_file:
        filters.add_filter(Specs.ls_lad_specific_file_dirs, ['fstab_mounted'])


def teardown_function(func):
    for spec in (
            Specs.ls_lad_specific_file_dirs,):
        if spec in filters._CACHE:
            del filters._CACHE[spec]


def test_fstab_mount_points():
    fstab_content = FSTab(context_wrap(FSTAB))

    broker = {
        FSTab: fstab_content
    }
    result = fstab_mounted(broker)
    assert result is not None
    assert result == '/ /boot /home swap'


def test_fstab_mount_points_bad():
    fstab_content = FSTab(context_wrap(FSTAB_EMPTY))

    broker = {
        FSTab: fstab_content
    }
    with pytest.raises(SkipComponent):
        fstab_mounted(broker)


def test_lad_specific_file():
    fstab_mount = Mock()
    fstab_mount.content = FSTAB_MOUNTED_CONTEXT.splitlines()
    broker = {Specs.fstab_mounted: fstab_mount}

    ret = list_with_lad_specific_file(broker)
    assert ret == '/ /boot /home swap'
