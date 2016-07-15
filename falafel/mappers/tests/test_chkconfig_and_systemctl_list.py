import unittest
from falafel.mappers.chkconfig_and_systemctl_list import enabled
from falafel.tests import context_wrap

SYSTEMCTL_ENBLED = """
{}                            enabled
"""

SYSTEMCTL_DISABLED = """
{}                            disabled
"""

SYSTEMCTL_STATIC = """
{}                            static
"""

CHKCONFIG_ON  = '{}	0:off	1:off	2:off	3:on	4:off	5:on	6:off'
CHKCONFIG_OFF = '{}	0:off	1:off	2:off	3:off	4:off	5:off	6:off'

class TestChkconfig(unittest.TestCase):
    def test_systemctl_enabled(self):
        for service in ["avahi-daemon", "oracleasm", "kdump"]:
            self.assertTrue(service in enabled(context_wrap(SYSTEMCTL_ENBLED.format(service))))
            self.assertFalse(service in enabled(context_wrap(SYSTEMCTL_DISABLED.format(service))))
            self.assertFalse(service in enabled(context_wrap(SYSTEMCTL_DISABLED.format(service))))
            self.assertTrue(service in enabled(context_wrap(CHKCONFIG_ON.format(service))))
            self.assertFalse(service in enabled(context_wrap(CHKCONFIG_OFF.format(service))))
