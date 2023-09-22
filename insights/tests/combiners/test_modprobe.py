from insights.parsers.modprobe import ModProbe
from insights.combiners.modprobe import AllModProbe, ModProbeValue
from insights.tests import context_wrap

MOD_OPTION_INFO = """
options ipv6 disable=1
install ipv6 /bin/true

# Test duplicate entry.
blacklist vfat
"""

MOD_OPTION_INFO_PATH = "/etc/modprobe.d/ipv6.conf"

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

# Test duplicate entry.
blacklist vfat
"""

MOD_COMPLETE_PATH = "/etc/modprobe.conf"


def test_all_modprobe():
    main_conf = ModProbe(context_wrap(MOD_COMPLETE, path=MOD_COMPLETE_PATH))
    subdir_cf = ModProbe(context_wrap(MOD_OPTION_INFO, path=MOD_OPTION_INFO_PATH))
    all_data = AllModProbe([main_conf, subdir_cf])

    # Test that all recognised options present, and knows where it came from.
    assert 'alias' in all_data
    assert all_data['alias'] == {
        'bnx2': ModProbeValue(value=['en*', 'eth*'], source=MOD_COMPLETE_PATH),
        'megaraid_sas': ModProbeValue(value=['scsi_hostadapter'], source=MOD_COMPLETE_PATH),
        'ata_piix': ModProbeValue(value=['scsi_hostadapter1'], source=MOD_COMPLETE_PATH),
    }

    assert 'blacklist' in all_data
    assert all_data['blacklist'] == {
        'i8xx_tco': ModProbeValue(value=True, source=MOD_COMPLETE_PATH),
        'vfat': ModProbeValue(value=True, source=MOD_OPTION_INFO_PATH),
    }

    assert 'install' in all_data
    assert all_data['install'] == {
        'eth1394': ModProbeValue(value=['/bin/true'], source=MOD_COMPLETE_PATH),
        'ipv6': ModProbeValue(value=['/bin/true'], source=MOD_OPTION_INFO_PATH),
        'usbmouse': ModProbeValue(
            value=['/sbin/modprobe', '--first-time', '--ignore-install', 'usbmouse', '&&', '{', '/sbin/modprobe', 'hid;', '/bin/true;', '}'],
            source=MOD_COMPLETE_PATH
        ),
    }

    assert 'options' in all_data
    assert all_data['options'] == {
        'bonding': ModProbeValue(value=['max_bonds=2'], source=MOD_COMPLETE_PATH),
        'bnx2': ModProbeValue(value=['disable_msi=1'], source=MOD_COMPLETE_PATH),
        'ipv6': ModProbeValue(value=['disable=1'], source=MOD_OPTION_INFO_PATH),
    }

    assert 'remove' in all_data
    assert all_data['remove'], {
        'usbmouse': ModProbeValue(
            value=['{', '/sbin/modprobe', '-r', 'hid;', '}', ';', '/sbin/modprobe', '-r', '--first-time', '--ignore-remove', 'usbmouse'],
            source=MOD_COMPLETE_PATH
        ),
    }

    assert "softdep" not in all_data

    # Test bad lines content
    assert len(all_data.bad_lines) == 3
    assert all_data.bad_lines[0] == ModProbeValue(value='alias', source=MOD_COMPLETE_PATH)
    assert all_data.bad_lines[1] == ModProbeValue(value='alias scsi_hostadapter2 ata_piix failed comment', source=MOD_COMPLETE_PATH)
    assert all_data.bad_lines[2] == ModProbeValue(value='balclkist ieee80211', source=MOD_COMPLETE_PATH)
