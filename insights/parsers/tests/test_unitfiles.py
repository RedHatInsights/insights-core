from ...tests import context_wrap
from ..systemd.unitfiles import UnitFiles

KDUMP_DISABLED_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               disabled
""".strip()

KDUMP_ENABLED_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               enabled
""".strip()

KDUMP_ENABLED_FOOTER_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               enabled
1 unit file listed.
""".strip()

KDUMP_BIG_TEST = """
UNIT FILE                                   STATE
kdump.service                               enabled
other.service                               disabled
test.service                                static

3 unit files listed.
""".strip()

UNIT_INVALID_VS_VALID = """
UNIT FILE                                   STATE
svca.service                                enabled
svcb.service                                masked
svcc.service                                somenonsense

3 unit files listed.
"""


def test_unitfiles():
    context = context_wrap(KDUMP_DISABLED_RHEL7)
    unitfiles = UnitFiles(context)
    assert not unitfiles.is_on('kdump.service')
    assert len(unitfiles.services) == 1
    assert len(unitfiles.parsed_lines) == 1

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('kdump.service')
    assert len(unitfiles.services) == 1
    assert len(unitfiles.parsed_lines) == 1

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('kdump.service')
    assert len(unitfiles.services) == 1
    assert len(unitfiles.parsed_lines) == 1

    context = context_wrap(KDUMP_BIG_TEST)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('kdump.service')
    assert not unitfiles.is_on('other.service')
    assert unitfiles.is_on('test.service')
    assert len(unitfiles.services) == 3
    assert len(unitfiles.parsed_lines) == 3

    context = context_wrap(UNIT_INVALID_VS_VALID)
    unitfiles = UnitFiles(context)
    assert unitfiles.is_on('svca.service')
    assert 'svca.service' in unitfiles.services
    assert 'svca.service' in unitfiles.service_list
    assert 'svcb.service' in unitfiles.services
    assert 'svcb.service' in unitfiles.service_list
    assert 'svcc.service' not in unitfiles.services
    assert 'svcc.service' not in unitfiles.service_list
    assert True is unitfiles.is_on('svca.service')
    assert False is unitfiles.is_on('svcb.service')
    assert None is unitfiles.is_on('svcc.service')
    assert unitfiles.exists('svca.service')
    assert unitfiles.exists('svcb.service')
    assert not unitfiles.exists('svcc.service')
