import doctest

from insights.combiners import lspci
from insights.combiners.lspci import LsPci
from insights.parsers.lspci import LsPci as LsPciParser, LsPciVmmkn
from insights.tests import context_wrap


LSPCI_K = """
00:00.0 Host bridge: Intel Corporation Haswell-ULT DRAM Controller (rev 09)
        Subsystem: Lenovo ThinkPad X240
        Kernel driver in use: hsw_uncore
00:02.0 VGA compatible controller: Intel Corporation Haswell-ULT Integrated Graphics Controller (rev 09)
        Subsystem: Lenovo ThinkPad X240
        Kernel driver in use: i915
        Kernel modules: i915
00:03.0 Audio device: Intel Corporation Haswell-ULT HD Audio Controller (rev 09)
        Subsystem: Lenovo ThinkPad X240
        Kernel driver in use: snd_hda_intel
        Kernel modules: snd_hda_intel
00:16.0 Communication controller: Intel Corporation 8 Series HECI #0 (rev 04)
        Subsystem: Lenovo ThinkPad X240
        Kernel driver in use: mei_me
        Kernel modules: mei_me
00:19.0 Ethernet controller: Intel Corporation Ethernet Connection I218-LM (rev 04)
        Subsystem: Lenovo ThinkPad X240
        Kernel driver in use: e1000e
        Kernel modules: e1000e
00:1b.0 Audio device: Intel Corporation 8 Series HD Audio Controller (rev 04)
        Subsystem: Lenovo ThinkPad X240
        Kernel driver in use: snd_hda_intel
        Kernel modules: snd_hda_intel
""".strip()

LSPCI_VMMKN = """

Slot:   00:00.0
Class:  0600
Vendor: 8086
Device: 0a04
SVendor:        17aa
SDevice:        2214
Rev:    09
Driver: hsw_uncore

Slot:   00:02.0
Class:  0300
Vendor: 8086
Device: 0a16
SVendor:        17aa
SDevice:        2214
Rev:    09
Driver: i915
Module: i915

Slot:   00:03.0
Class:  0403
Vendor: 8086
Device: 0a0c
SVendor:        17aa
SDevice:        2214
Rev:    09
Driver: snd_hda_intel
Module: snd_hda_intel

Slot:   00:16.0
Class:  0780
Vendor: 8086
Device: 9c3a
SVendor:        17aa
SDevice:        2214
Rev:    04
Driver: mei_me
Module: mei_me


Slot:   00:19.0
Class:  0200
Vendor: 8086
Device: 155a
SVendor:        17aa
SDevice:        2214
Rev:    04
Driver: e1000e
Module: e1000e

Slot:   00:1b.0
Class:  0403
Vendor: 8086
Device: 9c20
SVendor:        17aa
SDevice:        2214
Rev:    04
Driver: snd_hda_intel
Module: snd_hda_intel
"""

LSPCI_K_LONG_SLOT = """
0000:00:00.0 Host bridge: Intel Corporation 440BX/ZX/DX - 82443BX/ZX/DX Host bridge (AGP disabled) (rev 03)
0000:00:07.0 ISA bridge: Intel Corporation 82371AB/EB/MB PIIX4 ISA (rev 01)
        Subsystem: Microsoft Corporation Device 0000
0000:00:07.1 IDE interface: Intel Corporation 82371AB/EB/MB PIIX4 IDE (rev 01)
        Kernel driver in use: ata_piix
        Kernel modules: ata_piix, pata_acpi, ata_generic
0000:00:07.3 Bridge: Intel Corporation 82371AB/EB/MB PIIX4 ACPI (rev 02)
        Kernel modules: i2c_piix4
0000:00:08.0 VGA compatible controller: Microsoft Corporation Hyper-V virtual VGA
        Kernel driver in use: hyperv_fb
        Kernel modules: hyperv_fb
1a06:00:02.0 Ethernet controller: Mellanox Technologies MT27710 Family [ConnectX-4 Lx Virtual Function] (rev 80)
        Subsystem: Mellanox Technologies Device 0190
        Kernel driver in use: mlx5_core
        Kernel modules: mlx5_core
"""

LSPCI_VMMKN_LONG_SLOT = """
Slot:   00:00.0
Class:  0600
Vendor: 8086
Device: 7192
Rev:    03

Slot:   00:07.0
Class:  0601
Vendor: 8086
Device: 7110
SVendor:        1414
SDevice:        0000
Rev:    01

Slot:   00:07.1
Class:  0101
Vendor: 8086
Device: 7111
Rev:    01
ProgIf: 80
Driver: ata_piix
Module: ata_piix
Module: pata_acpi
Module: ata_generic

Slot:   00:07.3
Class:  0680
Vendor: 8086
Device: 7113
Rev:    02
Module: i2c_piix4

Slot:   00:08.0
Class:  0300
Vendor: 1414
Device: 5353
Driver: hyperv_fb
Module: hyperv_fb

Slot:   1a06:00:02.0
Class:  0200
Vendor: 15b3
Device: 1016
SVendor:        15b3
SDevice:        0190
PhySlot:        1
Rev:    80
Driver: mlx5_core
Module: mlx5_core
NUMANode:       0
"""


def test_lspci_k():
    lspci_k = LsPciParser(context_wrap(LSPCI_K))
    lspci = LsPci(lspci_k, None)
    assert sorted(lspci.pci_dev_list) == ['00:00.0', '00:02.0', '00:03.0', '00:16.0', '00:19.0', '00:1b.0']
    assert lspci.search(Dev_Details__contains='I218') == [
        {
            'Slot': '00:19.0',
            'Driver': 'e1000e', 'Module': ['e1000e'],
            'Subsystem': 'Lenovo ThinkPad X240',
            'Dev_Details': 'Ethernet controller: Intel Corporation Ethernet Connection I218-LM (rev 04)'
        }
    ]
    assert lspci.search(Slot__startwith='00:1b.0') == []
    # Make sure the original parser is untouched
    assert lspci_k.pci_dev_details('00:00.0').get('Kernel driver in use') == 'hsw_uncore'
    assert lspci_k.pci_dev_details('00:1b.0').get('Kernel driver in use') == 'snd_hda_intel'


def test_lspci_vmmkn():
    lspci_vmmkn = LsPciVmmkn(context_wrap(LSPCI_VMMKN))
    lspci = LsPci(None, lspci_vmmkn)
    assert sorted(lspci.pci_dev_list) == ['00:00.0', '00:02.0', '00:03.0', '00:16.0', '00:19.0', '00:1b.0']
    assert lspci.search(Device='155a', Vendor='8086') == [
        {
            'Slot': '00:19.0', 'Class': '0200', 'Vendor': '8086',
            'Device': '155a', 'SVendor': '17aa', 'SDevice': '2214',
            'Rev': '04', 'Driver': 'e1000e', 'Module': ['e1000e'],
        }
    ]
    assert lspci.search(Dev_Details__contains='I218') == []
    # Make sure the original parser is untouched
    assert sorted(lspci_vmmkn[0].keys()) == sorted(['Slot', 'Class', 'Vendor',
                        'Device', 'SVendor', 'SDevice', 'Rev', 'Driver'])


def test_lspci_both():
    lspci_vmmkn = LsPciVmmkn(context_wrap(LSPCI_VMMKN))
    lspci_k = LsPciParser(context_wrap(LSPCI_K))
    lspci = LsPci(lspci_k, lspci_vmmkn)
    assert sorted(lspci.pci_dev_list) == ['00:00.0', '00:02.0', '00:03.0', '00:16.0', '00:19.0', '00:1b.0']
    assert lspci.search(Dev_Details__contains='I218') == [
        {
            'Slot': '00:19.0', 'Class': '0200', 'Vendor': '8086',
            'Device': '155a', 'SVendor': '17aa', 'SDevice': '2214',
            'Rev': '04', 'Driver': 'e1000e', 'Module': ['e1000e'],
            'Subsystem': 'Lenovo ThinkPad X240',
            'Dev_Details': 'Ethernet controller: Intel Corporation Ethernet Connection I218-LM (rev 04)'
        }
    ]
    assert lspci.search(Slot='00:1b.0') == [
        {
            'Slot': '00:1b.0', 'Class': '0403', 'Vendor': '8086',
            'Device': '9c20', 'SVendor': '17aa', 'SDevice': '2214',
            'Rev': '04', 'Driver': 'snd_hda_intel',
            'Module': ['snd_hda_intel'],
            'Subsystem': 'Lenovo ThinkPad X240',
            'Dev_Details': 'Audio device: Intel Corporation 8 Series HD Audio Controller (rev 04)'
        }
    ]
    # Make sure the original parsers are untouched
    assert lspci_k.pci_dev_details('00:00.0').get('Kernel driver in use') == 'hsw_uncore'
    assert lspci_k.pci_dev_details('00:1b.0').get('Kernel driver in use') == 'snd_hda_intel'
    assert sorted(lspci_vmmkn[0].keys()) == sorted(['Slot', 'Class', 'Vendor',
            'Device', 'SVendor', 'SDevice', 'Rev', 'Driver'])
    assert sorted(lspci_vmmkn[-1].keys()) == sorted(['Class', 'Device',
            'Driver', 'Module', 'Rev', 'SDevice', 'SVendor', 'Slot', 'Vendor'])


def test_lspci_both_long_slot():
    lspci_vmmkn = LsPciVmmkn(context_wrap(LSPCI_VMMKN_LONG_SLOT))
    lspci_k = LsPciParser(context_wrap(LSPCI_K_LONG_SLOT))
    lspci = LsPci(lspci_k, lspci_vmmkn)
    assert sorted(lspci.pci_dev_list) == ['0000:00:00.0', '0000:00:07.0', '0000:00:07.1', '0000:00:07.3', '0000:00:08.0', '1a06:00:02.0']
    assert lspci.search(Dev_Details__contains='PIIX4 ISA') == [
        {
            'Slot': '0000:00:07.0', 'Class': '0601', 'Vendor': '8086',
            'Device': '7110', 'SVendor': '1414', 'SDevice': '0000',
            'Rev': '01',
            'Subsystem': 'Microsoft Corporation Device 0000',
            'Dev_Details': 'ISA bridge: Intel Corporation 82371AB/EB/MB PIIX4 ISA (rev 01)'
        }
    ]
    assert lspci.search(Slot='1a06:00:02.0') == [
        {
            'Slot': '1a06:00:02.0', 'Class': '0200', 'Vendor': '15b3',
            'Device': '1016', 'SVendor': '15b3', 'SDevice': '0190',
            'Rev': '80', 'Driver': 'mlx5_core', 'PhySlot': '1',
            'Module': ['mlx5_core'], 'NUMANode': '0',
            'Subsystem': 'Mellanox Technologies Device 0190',
            'Dev_Details': 'Ethernet controller: Mellanox Technologies MT27710 Family [ConnectX-4 Lx Virtual Function] (rev 80)'
        }
    ]
    # Make sure the original parsers are untouched
    assert sorted(lspci_k.pci_dev_list) == ['0000:00:00.0', '0000:00:07.0',
            '0000:00:07.1', '0000:00:07.3', '0000:00:08.0', '1a06:00:02.0']
    assert lspci_k.pci_dev_details('0000:00:00.0').get('Module') is None
    assert lspci_k.pci_dev_details('0000:00:08.0').get('Kernel driver in use') == 'hyperv_fb'
    assert sorted(lspci_vmmkn.pci_dev_list) == ['00:00.0', '00:07.0', '00:07.1', '00:07.3', '00:08.0', '1a06:00:02.0']
    assert sorted(lspci_vmmkn[0].keys()) == sorted(['Class', 'Device', 'Rev', 'Slot', 'Vendor'])
    assert sorted(lspci_vmmkn[-1].keys()) == sorted(['Class', 'Device',
            'Driver', 'Module', 'Rev', 'SDevice', 'SVendor', 'Slot', 'Vendor',
            'PhySlot', 'NUMANode'])


def test_doc_examples():
    lspci_vmmkn = LsPciVmmkn(context_wrap(LSPCI_VMMKN))
    lspci_k = LsPciParser(context_wrap(LSPCI_K))
    env = {'lspci': LsPci(lspci_k, lspci_vmmkn)}
    failed, total = doctest.testmod(lspci, globs=env)
    assert failed == 0
