from falafel.tests import context_wrap

from falafel.mappers.systemd import unitfiles

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
    uf = unitfiles.UnitFiles.parse_context(context)
    assert not uf.is_on('kdump.service')
    assert len(uf.data) == 1

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    uf = unitfiles.UnitFiles.parse_context(context)
    print uf.data
    assert uf.is_on('kdump.service')
    assert len(uf.data) == 1

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    uf = unitfiles.UnitFiles.parse_context(context)
    assert uf.is_on('kdump.service')
    assert len(uf.data) == 1

    context = context_wrap(KDUMP_BIG_TEST)
    uf = unitfiles.UnitFiles.parse_context(context)
    assert uf.is_on('kdump.service')
    assert not uf.is_on('other.service')
    assert uf.is_on('test.service')
    assert len(uf.data) == 3
