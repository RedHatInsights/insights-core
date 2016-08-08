import unittest

from falafel.mappers.modprobe import modprobe
from falafel.tests import context_wrap

MOD_OPTION_INFO = """
options ipv6 disable=1
options mlx4_core debug_level=1 log_num_mgm_entry_size=-1

install ipv6 /bin/true
""".strip()

MODPROBE_CONF = """
options ipv6 disable=1
options mlx4_core debug_level=1 log_num_mgm_entry_size=-1

install ipv6 /bin/true
""".strip()

MODPROBE_CONF_PATH = "etc/modprobe.conf"

MOD_OPTION_INFO_PATH = "etc/modprobe.d/ipv6.conf"


class TestNproc(unittest.TestCase):
    def test_modprobe_v1(self):
        modprobe_info = modprobe(context_wrap(MOD_OPTION_INFO,
                                            path=MOD_OPTION_INFO_PATH))
        assert modprobe_info["options"].get('ipv6') == ['disable=1']
        assert modprobe_info["options"].get('mlx4_core')[0] == 'debug_level=1'
        assert modprobe_info["install"].get('ipv6') == ['/bin/true']

    def test_modprobe_v2(self):
        modprobe_info = modprobe(context_wrap(MODPROBE_CONF,
                                            path=MODPROBE_CONF_PATH))
        assert modprobe_info["options"].get('ipv6') == ['disable=1']
        assert modprobe_info["options"].get('mlx4_core')[0] == 'debug_level=1'
        assert modprobe_info["install"].get('ipv6') == ['/bin/true']
