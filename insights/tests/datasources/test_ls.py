import pytest

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.specs import Specs
from insights.specs.datasources.ls import (
        list_with_la, list_with_la_filtered,
        list_with_lan, list_with_lan_filtered,
        list_with_lanL, list_with_lanR, list_with_lanRL,
        list_with_lanRZ, list_with_lanZ)


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
        filters.add_filter(Specs.ls_lanRZ_dirs, ['/boot'])
    if func is test_lanZ:
        filters.add_filter(Specs.ls_lanZ_dirs, ["/", '/mnt'])


def teardown_function(func):
    for spec in (
            Specs.ls_la_dirs, Specs.ls_la_filtered, Specs.ls_la_filtered_dirs,
            Specs.ls_lan_dirs, Specs.ls_lan_filtered, Specs.ls_lan_filtered_dirs,
            Specs.ls_lanL_dirs, Specs.ls_lanR_dirs, Specs.ls_lanRL_dirs,
            Specs.ls_lanRZ_dirs, Specs.ls_lanZ_dirs):
        if spec in filters._CACHE:
            del filters._CACHE[spec]


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
    assert '/ ' in ret


def test_lanRL():
    ret = list_with_lanRL({})
    assert ret == '/ /boot'


def test_lanRZ():
    ret = list_with_lanRZ({})
    assert ret == '/boot'


def test_lanZ():
    ret = list_with_lanZ({})
    assert ret == '/ /mnt'
