import unittest

from falafel.mappers.ethtool import Driver
from falafel.tests import context_wrap

GOOD = """
driver: virtio_net
version: 1.0.0
firmware-version:
bus-info: 0000:00:03.0
supports-statistics: no
supports-test: no
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: no
"""

MISSING_KEYS = """
driver: virtio_net
firmware-version:
bus-info: 0000:00:03.0
supports-statistics: no
supports-test: no
supports-eeprom-access: no
supports-register-dump: no
supports-priv-flags: no
"""


class TestEthtoolI(unittest.TestCase):

    def test_good(self):
        context = context_wrap(GOOD)
        parsed = Driver.parse_context(context)
        assert parsed.version == "1.0.0"

    def test_missing_version(self):
        context = context_wrap(MISSING_KEYS)
        parsed = Driver.parse_context(context)
        assert parsed.version is None

    def test_missing_value(self):
        context = context_wrap(GOOD)
        parsed = Driver.parse_context(context)
        assert parsed.firmware_version is None

    def test_iface(self):
        context = context_wrap(GOOD, path="foo/bar/baz/ethtool_-i_eth0")
        parsed = Driver.parse_context(context)
        assert parsed.ifname == "eth0"

    def test_no_iface(self):
        context = context_wrap(GOOD, path="foo/bar/baz/oopsie")
        parsed = Driver.parse_context(context)
        assert parsed.ifname is None
