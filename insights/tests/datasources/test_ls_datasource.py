from insights.core import filters
from insights.specs import Specs
from insights.specs.datasources.ls_datasource import list_with_lad_specific_file
from mock.mock import Mock

FSTAB_MOUNTED_CONTEXT = '/ /boot /home swap'


def setup_function(func):
    if func is test_lad_specific_file:
        filters.add_filter(Specs.ls_lad_specific_file_dirs, ['fstab_mounted'])


def teardown_function(func):
    for spec in (
            Specs.ls_lad_specific_file_dirs,):
        if spec in filters._CACHE:
            del filters._CACHE[spec]


def test_lad_specific_file():
    fstab_mount = Mock()
    fstab_mount.content = FSTAB_MOUNTED_CONTEXT.splitlines()
    broker = {Specs.fstab_mounted: fstab_mount}

    ret = list_with_lad_specific_file(broker)
    assert ret == '/ /boot /home swap'
