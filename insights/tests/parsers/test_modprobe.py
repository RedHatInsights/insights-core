from insights.parsers.modprobe import ModProbe
from insights.tests import context_wrap

MODPROBE_CONF = """
options ipv6 disable=1
options mlx4_core debug_level=1 log_num_mgm_entry_size=-1

install ipv6 /bin/true
""".strip()

MODPROBE_CONF_PATH = "etc/modprobe.conf"

MOD_OPTION_INFO = """
options ipv6 disable=1
options mlx4_core debug_level=1 log_num_mgm_entry_size=-1

install ipv6 /bin/true
""".strip()

MOD_OPTION_INFO_PATH = "etc/modprobe.d/ipv6.conf"

MOD_COMPLETE = """
#
# Syntax: see modprobe.conf(5).
#

# aliases
alias en* bnx2
alias eth* bnx2
alias scsi_hostadapter megaraid_sas
alias scsi_hostadapter1 ata_piix

# watchdog drivers
blacklist i8xx_tco

# Don't install the Firewire ethernet driver
install eth1394 /bin/true

# Special handling for USB mouse
install usbmouse /sbin/modprobe --first-time --ignore-install usbmouse && { /sbin/modprobe hid; /bin/true; }
remove usbmouse { /sbin/modprobe -r hid; } ; /sbin/modprobe -r --first-time --ignore-remove usbmouse

# bonding options
options bonding max_bonds=2
options bnx2 disable_msi=1

# Test bad data - save in bad_lines
alias
alias scsi_hostadapter2 ata_piix failed comment
balclkist ieee80211
""".strip()

MOD_COMPLETE_PATH = "etc/modprobe.conf"


def test_modprobe_v1():
    modprobe_info = ModProbe(context_wrap(MOD_OPTION_INFO,
                                          path=MOD_OPTION_INFO_PATH))
    assert modprobe_info["options"].get('ipv6') == ['disable=1']
    assert modprobe_info["options"].get('mlx4_core')[0] == 'debug_level=1'
    assert modprobe_info["install"].get('ipv6') == ['/bin/true']


def test_modprobe_v2():
    modprobe_info = ModProbe(context_wrap(MODPROBE_CONF,
                                          path=MODPROBE_CONF_PATH))
    assert modprobe_info["options"].get('ipv6') == ['disable=1']
    assert modprobe_info["options"].get('mlx4_core')[0] == 'debug_level=1'
    assert modprobe_info["install"].get('ipv6') == ['/bin/true']


def test_modprobe_complete():
    minfo = ModProbe(context_wrap(MOD_COMPLETE, path=MOD_COMPLETE_PATH))
    assert sorted(minfo.data.keys()) == sorted([
        'alias', 'blacklist', 'install', 'options', 'remove'
    ])
    assert sorted(minfo['alias']['bnx2']) == sorted(['eth*', 'en*'])
    assert 'i8xx_tco' in minfo['blacklist']
    assert minfo['blacklist']['i8xx_tco'] is True
    assert minfo['install']['eth1394'] == ['/bin/true']
    assert 'usbmouse' in minfo['install']
    assert 'usbmouse' in minfo['remove']
    assert minfo['options']['bonding'] == ['max_bonds=2']
    assert minfo['options']['bnx2'] == ['disable_msi=1']

    # Test that we get bad lines
    assert len(minfo.bad_lines) == 3
    assert minfo.bad_lines[0] == 'alias'
    assert minfo.bad_lines[1] == 'alias scsi_hostadapter2 ata_piix failed comment'
    assert minfo.bad_lines[2] == 'balclkist ieee80211'
