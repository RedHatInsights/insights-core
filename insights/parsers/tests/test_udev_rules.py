import doctest
from insights.parsers import udev_rules
from insights.parsers.udev_rules import UdevRules
from insights.tests import context_wrap

UDEV_RULES_FILT_HIT = """
#
# FC WWPN-based by-path links
#

ACTION!="add|change", GOTO="fc_wwpn_end"
KERNEL!="sd*", GOTO="fc_wwpn_end"

ENV{DEVTYPE}=="disk", IMPORT{program}="fc_wwpn_id %p"
ENV{DEVTYPE}=="partition", IMPORT{parent}="FC_*"
ENV{FC_TARGET_WWPN}!="$*"; GOTO="fc_wwpn_end"
ENV{FC_INITIATOR_WWPN}!="$*"; GOTO="fc_wwpn_end"
ENV{FC_TARGET_LUN}!="$*"; GOTO="fc_wwpn_end"

ENV{DEVTYPE}=="disk", SYMLINK+="disk/by-path/fc-$env{FC_INITIATOR_WWPN}-$env{FC_TARGET_WWPN}-lun-$env{FC_TARGET_LUN}"
ENV{DEVTYPE}=="partition", SYMLINK+="disk/by-path/fc-$env{FC_INITIATOR_WWPN}-$env{FC_TARGET_WWPN}-lun-$env{FC_TARGET_LUN}-part%n"

LABEL="fc_wwpn_end"
""".strip()

UDEV_RULES_FILT_NOT_HIT = """
#
# FC WWPN-based by-path links
#

ACTION!="add|change",GOTO="fc_wwpn_end"
KERNEL!="sd*",GOTO="fc_wwpn_end"

ENV{DEVTYPE}=="disk",IMPORT{program}="fc_wwpn_id %p"
ENV{DEVTYPE}=="partition",IMPORT{parent}="FC_*"
ENV{FC_TARGET_WWPN}!="$*",GOTO="fc_wwpn_end"
ENV{FC_INITIATOR_WWPN}!="$*",GOTO="fc_wwpn_end"
ENV{FC_TARGET_LUN}!="$*",GOTO="fc_wwpn_end"
LABEL="fc_wwpn_end"
""".strip()

UDEV_RULES_FILT_NOT_HIT_2 = """
ACTION!="add|change|move", GOTO="mm_zte_port_types_end"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="19d2", GOTO="mm_zte_port_types"
GOTO="mm_zte_port_types_end"

LABEL="mm_zte_port_types"

SUBSYSTEMS=="usb", ATTRS{bInterfaceNumber}=="?*", ENV{.MM_USBIFNUM}="$attr{bInterfaceNumber}"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0001", ENV{.MM_USBIFNUM}=="00", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0001", ENV{.MM_USBIFNUM}=="02", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0002", ENV{.MM_USBIFNUM}=="02", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0002", ENV{.MM_USBIFNUM}=="04", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0003", ENV{.MM_USBIFNUM}=="00", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0003", ENV{.MM_USBIFNUM}=="01", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0004", ENV{.MM_USBIFNUM}=="00", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0004", ENV{.MM_USBIFNUM}=="01", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0005", ENV{.MM_USBIFNUM}=="00", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0005", ENV{.MM_USBIFNUM}=="01", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0006", ENV{.MM_USBIFNUM}=="00", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0006", ENV{.MM_USBIFNUM}=="01", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"

ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0007", ENV{.MM_USBIFNUM}=="00", ENV{ID_MM_ZTE_PORT_TYPE_MODEM}="1"
ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0007"; ENV{.MM_USBIFNUM}=="01", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"
"""


def test_documentation():
    env = {'udev_rules': UdevRules(context_wrap(UDEV_RULES_FILT_NOT_HIT))}
    failed_count, tests = doctest.testmod(udev_rules, globs=env)
    assert failed_count == 0


def test_udev_rules():
    result = UdevRules(context_wrap(UDEV_RULES_FILT_HIT))
    assert not result.file_valid
    print(result.invalid_lines)
    for line in ['ENV{FC_TARGET_WWPN}!="$*"; GOTO="fc_wwpn_end"',
                 'ENV{FC_INITIATOR_WWPN}!="$*"; GOTO="fc_wwpn_end"',
                  'ENV{FC_TARGET_LUN}!="$*"; GOTO="fc_wwpn_end"']:
        assert line in result.invalid_lines

    result = UdevRules(context_wrap(UDEV_RULES_FILT_NOT_HIT_2))
    assert not result.file_valid
    assert 'ATTRS{idVendor}=="19d2", ATTRS{idProduct}=="0007"; ENV{.MM_USBIFNUM}=="01", ENV{ID_MM_ZTE_PORT_TYPE_AUX}="1"' in result.invalid_lines
