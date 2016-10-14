import unittest

from falafel.mappers.chkconfig import ChkConfig
from falafel.mappers.systemd.unitfiles import UnitFiles
from falafel.reducers.services import Services
from falafel.tests import context_wrap

CHKCONFIG_OFF = 'kdump	0:off	1:off	2:off	3:off	4:off	5:off	6:off'

CHKCONFIG_ON = 'kdump	0:off	1:off	2:off	3:on	4:off	5:on	6:off'

KDUMP_DISABLED_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               disabled
""".strip()

KDUMP_ENABLED_RHEL7 = """
UNIT FILE                                   STATE
kdump.service                               enabled
""".strip()


class TestServices(unittest.TestCase):
    def test_chkconfig_on(self):
        cfg = ChkConfig(context_wrap(CHKCONFIG_ON))
        s = Services(None, {ChkConfig: cfg, UnitFiles: None})
        self.assertTrue(s.is_on('kdump'))

    def test_chkconfig_off(self):
        cfg = ChkConfig(context_wrap(CHKCONFIG_OFF))
        s = Services(None, {ChkConfig: cfg, UnitFiles: None})
        self.assertFalse(s.is_on('kdump'))

    def test_unitfiles_on(self):
        context = context_wrap(KDUMP_ENABLED_RHEL7)
        uf = UnitFiles(context)
        s = Services(None, {ChkConfig: None, UnitFiles: uf})
        self.assertTrue(s.is_on('kdump'))

    def test_unitfiles_off(self):
        context = context_wrap(KDUMP_DISABLED_RHEL7)
        uf = UnitFiles(context)
        s = Services(None, {ChkConfig: None, UnitFiles: uf})
        self.assertFalse(s.is_on('kdump'))
