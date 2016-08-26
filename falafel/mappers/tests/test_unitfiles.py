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


def test_unitfiles():
    context = context_wrap(KDUMP_DISABLED_RHEL7)
    uf = unitfiles.UnitFiles.parse_context(context)
    print uf.data
    assert not uf.is_on('kdump.service')

    context = context_wrap(KDUMP_ENABLED_RHEL7)
    uf = unitfiles.UnitFiles.parse_context(context)
    print uf.data
    assert uf.is_on('kdump.service')
