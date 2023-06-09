import pytest

from insights.core import filters
from insights.core.exceptions import SkipComponent
from insights.parsers.lsmod import LsMod
from insights.specs import Specs
from insights.specs.datasources.kernel_module_list import kernel_module_filters
from insights.tests import context_wrap

LSMOD = """
Module                  Size  Used by
igb                   249856  0
i2c_algo_bit           16384  1 igb
dca                    16384  1 igb
binfmt_misc            20480  1
tcp_diag               16384  0
udp_diag               16384  0
inet_diag              24576  2 tcp_diag,udp_diag
binfmt_misc            69632  0
udp_diag               18632  0
mfe_aac_100713183      23360   0
mfe_aac_100712495       3360   0
""".strip()

LSMOD_NO_LOADED = """
Module                  Size  Used by
tcp_diag               16384  0
""".strip()


def setup_function(func):
    if Specs.modinfo_modules in filters._CACHE:
        del filters._CACHE[Specs.modinfo_modules]
    if Specs.modinfo_modules in filters.FILTERS:
        del filters.FILTERS[Specs.modinfo_modules]

    if func is test_module_filters:
        filters.add_filter(Specs.modinfo_modules, ["udp_diag", "binfmt_misc", "wireguard"])
    if func is test_module_filters_2:
        filters.add_filter(Specs.modinfo_modules, ["mfe_aac"])
    if func is test_module_no_loaded_modules:
        filters.add_filter(Specs.modinfo_modules, ["udp_diag", "binfmt_misc", "wireguard"])
    if func is test_module_filters_empty:
        filters.add_filter(Specs.modinfo_modules, [])


def test_module_filters():
    lsmod_info = LsMod(context_wrap(LSMOD))
    broker = {LsMod: lsmod_info}
    result = kernel_module_filters(broker)
    assert 'binfmt_misc udp_diag' == result


def test_module_filters_2():
    lsmod_info = LsMod(context_wrap(LSMOD))
    broker = {LsMod: lsmod_info}
    result = kernel_module_filters(broker)
    assert 'mfe_aac_100713183 mfe_aac_100712495' == result


def test_module_filters_empty():
    lsmod_info = LsMod(context_wrap(LSMOD))
    broker = {LsMod: lsmod_info}
    with pytest.raises(SkipComponent):
        kernel_module_filters(broker)


def test_module_no_loaded_modules():
    lsmod_info = LsMod(context_wrap(LSMOD_NO_LOADED))
    broker = {LsMod: lsmod_info}
    with pytest.raises(SkipComponent):
        kernel_module_filters(broker)
