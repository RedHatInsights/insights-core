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


def test_lspci_k():
    lspci_k = LsPciParser(context_wrap(LSPCI_K))
    lspci = LsPci(lspci_k, None)
    assert sorted(lspci.pci_dev_list) == ['00:00.0', '00:02.0', '00:03.0', '00:16.0', '00:19.0', '00:1b.0']
    assert lspci.search(Dev_Details__contains='I218') == [
        {
            'Driver': 'e1000e', 'Module': ['e1000e'],
            'Subsystem': 'Lenovo ThinkPad X240',
            'Dev_Details': 'Ethernet controller: Intel Corporation Ethernet Connection I218-LM (rev 04)'
        }
    ]
    assert lspci.search(Slot__startwith='00:1b.0') == []


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


def test_doc_examples():
    lspci_vmmkn = LsPciVmmkn(context_wrap(LSPCI_VMMKN))
    lspci_k = LsPciParser(context_wrap(LSPCI_K))
    env = {'lspci': LsPci(lspci_k, lspci_vmmkn)}
    failed, total = doctest.testmod(lspci, globs=env)
    assert failed == 0
