from falafel.mappers.modprobe_d import modprobe
from falafel.tests import context_wrap

MOD_OPTION_INFO = """
options ipv6 disable=1
options mlx4_core debug_level=1 log_num_mgm_entry_size=-1

install ipv6 /bin/true
""".strip()


def test_modprobe():
    modprobe_info = modprobe(context_wrap(MOD_OPTION_INFO))
    assert modprobe_info.options_dict.get('ipv6') == ['disable=1']
    assert modprobe_info.options_dict.get('mlx4_core')[0] == 'debug_level=1'
    assert modprobe_info.install_dict.get('ipv6') == ['/bin/true']
