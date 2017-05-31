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
