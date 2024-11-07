import pytest

from collections import defaultdict

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.parsers.fstab import FSTab
from insights.specs import Specs
from insights.specs.datasources.ls import (
        list_with_la, list_with_la_filtered,
        list_with_lan, list_with_lan_filtered,
        list_with_lanL, list_with_lanR, list_with_lanRL,
        list_with_laRZ, list_with_laZ)
from insights.tests import context_wrap


FSTAB_CONTEXT = """
/dev/mapper/rhel_rhel8-root /                       xfs     defaults        0 0
/dev/vda1 /boot                   xfs     defaults        0 0
/dev/mapper/rhel_rhel8-swap none                    swap    defaults        0 0
/dev/mapper/rhel_rhel7-hana1 /hana/data/rhel7-hana1                       xfs     defaults        0 0
/dev/mapper/rhel_rhel7-hana2 /hana/data/rhel7-hana2                       xfs     defaults        0 0
/dev/mapper/rhel_rhel7-hana3 /hana/data/rhel7-hana3                       xfs     defaults        0 0
""".strip()


def setup_function(func):
    if func is test_la_empty:
        pass
    if func is test_la:
        filters.add_filter(Specs.ls_la_dirs, ["/"])
    if func is test_la_filterd:
        filters.add_filter(Specs.ls_la_filtered_dirs, ["/", '/boot'])
    if func is test_lan:
        filters.add_filter(Specs.ls_lan_dirs, ["/", '/boot'])
    if func is test_lan_filterd:
        filters.add_filter(Specs.ls_lan_filtered_dirs, ["/"])
    if func is test_lanL:
        filters.add_filter(Specs.ls_lanL_dirs, ["/", '/boot'])
    if func is test_lanR:
        filters.add_filter(Specs.ls_lanR_dirs, ["/"])
    if func is test_lanRL:
        filters.add_filter(Specs.ls_lanRL_dirs, ["/", '/boot'])
    if func is test_lanRZ:
        filters.add_filter(Specs.ls_laRZ_dirs, ['/boot'])
    if func is test_lanZ:
        filters.add_filter(Specs.ls_laZ_dirs, ["/", '/mnt'])
    if func is test_lan_with_fstab_mounted_filter:
        filters.add_filter(Specs.ls_lan_dirs, ["/", '/boot', 'fstab_mounted.dirs'])


def teardown_function(func):
    filters._CACHE = {}
    filters.FILTERS = defaultdict(set)


def test_la_empty():
    with pytest.raises(SkipComponent):
        list_with_la({})


def test_la():
    ret = list_with_la({})
    assert ret == '/ _non_existing_'


def test_la_filterd():
    ret = list_with_la_filtered({})
    assert ret == '/ /boot'


def test_lan():
    ret = list_with_lan({})
    assert ret == '/ /boot'


def test_lan_filterd():
    ret = list_with_lan_filtered({})
    assert ret == '/ _non_existing_'


def test_lanL():
    ret = list_with_lanL({})
    assert ret == '/ /boot'


def test_lanR():
    ret = list_with_lanR({})
    assert '/' == ret


def test_lanRL():
    ret = list_with_lanRL({})
    assert ret == '/ /boot'


def test_lanRZ():
    ret = list_with_laRZ({})
    assert ret == '/boot'


def test_lanZ():
    ret = list_with_laZ({})
    assert ret == '/ /mnt'


def test_lan_with_fstab_mounted_filter():
    fstab = FSTab(context_wrap(FSTAB_CONTEXT))
    broker = {
        FSTab: fstab
    }
    ret = list_with_lan(broker)
    assert ret == '/ /boot /hana/data fstab_mounted.dirs'
