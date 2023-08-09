import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import lspci
from insights.parsers.lspci import LsPci, LsPciVmmkn
from insights.tests import context_wrap


LSPCI_0 = """
00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)
00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
0d:00.0 System peripheral: Ricoh Co Ltd PCIe SDXC/MMC Host Controller (rev 07)
""".strip()


INTEL = """
00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)
00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
""".strip()

OTHER = """
05:00.0 PCI bridge: Renesas Technology Corp. Device 001d
06:00.0 PCI bridge: Renesas Technology Corp. Device 001d
07:00.0 PCI bridge: Renesas Technology Corp. Device 001a
7f:14.4 System peripheral: Intel Corporation Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
7f:14.5 System peripheral: Intel Corporation Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
7f:14.6 System peripheral: Intel Corporation Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
7f:14.7 System peripheral: Intel Corporation Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
""".strip()

RENESAS = """
05:00.0 PCI bridge: Renesas Technology Corp. Device 001d
06:00.0 PCI bridge: Renesas Technology Corp. Device 001d
07:00.0 PCI bridge: Renesas Technology Corp. Device 001a
""".strip()


LSPCI_DRIVER_DETAILS = """
00:00.0 Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
00:01.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 1 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:02.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 2 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:03.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 3 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:07.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 7 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:08.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 8 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:09.0 PCI bridge: Intel Corporation 7500/5520/5500/X58 I/O Hub PCI Express Root Port 9 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:0a.0 PCI bridge: Intel Corporation 7500/5520/5500/X58 I/O Hub PCI Express Root Port 10 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:10.0 PIC: Intel Corporation 7500/5520/5500/X58 Physical and Link Layer Registers Port 0 (rev 13)
        Subsystem: Device 0037:0001
00:10.1 PIC: Intel Corporation 7500/5520/5500/X58 Routing and Protocol Layer Registers Port 0 (rev 13)
        Subsystem: Device 0037:0001
00:11.0 PIC: Intel Corporation 7500/5520/5500 Physical and Link Layer Registers Port 1 (rev 13)
        Subsystem: Device 0037:0001
00:11.1 PIC: Intel Corporation 7500/5520/5500 Routing & Protocol Layer Register Port 1 (rev 13)
        Subsystem: Device 0037:0001
00:13.0 PIC: Intel Corporation 7500/5520/5500/X58 I/O Hub I/OxAPIC Interrupt Controller (rev 13)
        Subsystem: Device 0037:0001
00:14.0 PIC: Intel Corporation 7500/5520/5500/X58 I/O Hub System Management Registers (rev 13)
        Subsystem: Device 0037:0001
        Kernel modules: i7core_edac
00:14.1 PIC: Intel Corporation 7500/5520/5500/X58 I/O Hub GPIO and Scratch Pad Registers (rev 13)
        Subsystem: Device 0037:0001
00:14.2 PIC: Intel Corporation 7500/5520/5500/X58 I/O Hub Control Status and RAS Registers (rev 13)
        Subsystem: Device 0037:0001
00:14.3 PIC: Intel Corporation 7500/5520/5500/X58 I/O Hub Throttle Registers (rev 13)
        Subsystem: Device 0037:0001
00:16.0 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.1 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.2 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.3 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.4 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.5 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.6 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:16.7 System peripheral: Intel Corporation 5520/5500/X58 Chipset QuickData Technology Device (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ioatdma
        Kernel modules: ioatdma
00:1a.0 USB controller: Intel Corporation 82801JI (ICH10 Family) USB UHCI Controller #4
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: uhci_hcd
00:1a.1 USB controller: Intel Corporation 82801JI (ICH10 Family) USB UHCI Controller #5
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: uhci_hcd
00:1a.2 USB controller: Intel Corporation 82801JI (ICH10 Family) USB UHCI Controller #6
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: uhci_hcd
00:1a.7 USB controller: Intel Corporation 82801JI (ICH10 Family) USB2 EHCI Controller #2
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ehci_hcd
00:1c.0 PCI bridge: Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 1
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:1c.4 PCI bridge: Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 5
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:1c.5 PCI bridge: Intel Corporation 82801JI (ICH10 Family) PCI Express Root Port 6
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:1d.0 USB controller: Intel Corporation 82801JI (ICH10 Family) USB UHCI Controller #1
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: uhci_hcd
00:1d.1 USB controller: Intel Corporation 82801JI (ICH10 Family) USB UHCI Controller #2
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: uhci_hcd
00:1d.2 USB controller: Intel Corporation 82801JI (ICH10 Family) USB UHCI Controller #3
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: uhci_hcd
00:1d.7 USB controller: Intel Corporation 82801JI (ICH10 Family) USB2 EHCI Controller #1
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: ehci_hcd
00:1e.0 PCI bridge: Intel Corporation 82801 PCI Bridge (rev 90)
00:1f.0 ISA bridge: Intel Corporation 82801JIR (ICH10R) LPC Interface Controller
        Subsystem: Cisco Systems Inc Device 0101
        Kernel driver in use: lpc_ich
        Kernel modules: lpc_ich
01:00.0 SCSI storage controller: LSI Logic / Symbios Logic SAS1064ET PCI-Express Fusion-MPT SAS (rev 08)
        Subsystem: Cisco Systems Inc Device 0049
        Kernel driver in use: mptsas
        Kernel modules: mptsas
04:00.0 Fibre Channel: QLogic Corp. ISP2432-based 4Gb Fibre Channel to PCI Express HBA (rev 03)
        Subsystem: Cisco Systems Inc Device 004a
        Kernel driver in use: qla2xxx
        Kernel modules: qla2xxx
04:00.1 Fibre Channel: QLogic Corp. ISP2432-based 4Gb Fibre Channel to PCI Express HBA (rev 03)
        Subsystem: Cisco Systems Inc Device 004a
        Kernel driver in use: qla2xxx
        Kernel modules: qla2xxx
06:00.0 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
        Subsystem: Cisco Systems Inc Device 004a
        Kernel driver in use: ixgbe
        Kernel modules: ixgbe
06:00.1 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
        Subsystem: Cisco Systems Inc Device 004a
        Kernel driver in use: ixgbe
        Kernel modules: ixgbe
09:00.0 VGA compatible controller: Matrox Electronics Systems Ltd. MGA G200e [Pilot] ServerEngines (SEP1) (rev 02)
        Subsystem: Cisco Systems Inc Device 0101
""".strip()

LSPCI_DRIVER_DETAILS_2 = """
04:00.0 Fibre Channel: QLogic Corp. ISP2432-based 4Gb Fibre Channel to PCI Express HBA (rev 03)
04:00.1 Fibre Channel: QLogic Corp. ISP2432-based 4Gb Fibre Channel to PCI Express HBA (rev 03)
06:00.1 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
09:00.0 VGA compatible controller: Matrox Electronics Systems Ltd. MGA G200e [Pilot] ServerEngines (SEP1) (rev 02)
VGA compatible controller: Matrox Electronics Systems Ltd:MGA G200e [Pilot] ServerEngines (SEP1) (rev 02)
""".strip()

LSPCI_DRIVER_DETAILS_3 = """
Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
VGA compatible controller: Matrox Electronics Systems Ltd:MGA G200e [Pilot] ServerEngines (SEP1) (rev 02)
""".strip()

LSPCI_DRIVER_DOC = """
00:00.0 Host bridge: Intel Corporation 5500 I/O Hub to ESI Port (rev 13)
        Subsystem: Cisco Systems Inc Device 0101
00:01.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 1 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
00:02.0 PCI bridge: Intel Corporation 5520/5500/X58 I/O Hub PCI Express Root Port 2 (rev 13)
        Kernel driver in use: pcieport
        Kernel modules: shpchp
03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
        Subsystem: Cisco Systems Inc Device 004a
        Kernel driver in use: ixgbe
        Kernel modules: ixgbe
06:00.0 Ethernet controller: Intel Corporation 82598EB 10-Gigabit AF Dual Port Network Connection (rev 01)
        Subsystem: Cisco Systems Inc Device 004a
        Kernel driver in use: ixgbe
        Kernel modules: ixgbe
""".strip()

LSPCI_OUTPUT_WITH_BAD_LINES = """
03:00.0 Network controller: Intel Corporation Wireless 7260 (rev bb)
        Subsystem: Intel Corporation Dual Band Wireless-AC 7260

        Kernel driver in use: iwlwifi
# a comment
        Kernel modules: iwlwifi
""".strip()

LSPCI_VMMKN = """
Slot:   00:00.0
Class:  0600
Vendor: 8086
Device: 1237
SVendor:    1af4
SDevice:    1100
Rev:    02

Slot:   00:01.0
Class:  0101
Vendor: 8086
Device: 7010
SVendor:    1af4
SDevice:    1100
ProgIf: 80
Driver: ata_piix
Module: ata_piix
Module: ata_generic

Slot:   00:01.1
Class:  0c03
Vendor: 8086
Device: 7020
SVendor:    1af4
SDevice:    1100
Rev:    01
Driver: uhci_hcd


Slot:   00:03.0
Class:  0200
Vendor: 1af4
Device: 1000
SVendor:    1af4
SDevice:    0001
PhySlot:    3
Driver: virtio-pci
""".strip()


def test_lspci():
    LsPci.token_scan('centrino', 'Centrino')
    lspci_0 = LsPci(context_wrap(LSPCI_0))
    assert [i['raw_message'] for i in lspci_0.get("Intel Corporation")] == INTEL.splitlines()
    assert len(lspci_0.get("Network controller")) == 1
    assert "Centrino Advanced-N 6205" in lspci_0
    assert "0d:00.0" in lspci_0
    other = LsPci(context_wrap(OTHER))
    assert [i['raw_message'] for i in other.get("Renesas Technology Corp.")] == RENESAS.splitlines()
    assert len(other.get("Xeon E5 v3")) == 4
    assert len(other.get("001a")) == 1
    assert "Core i7" in other


def test_lspci_driver():
    lspci_obj = LsPci(context_wrap(LSPCI_DRIVER_DETAILS))
    assert len(lspci_obj.data) == 44
    dev_info = lspci_obj.pci_dev_details('00:01.0')
    assert len(dev_info) == 4
    assert dev_info['Kernel driver in use'] == 'pcieport'
    assert dev_info['Slot'] == '00:01.0'
    assert len(lspci_obj.pci_dev_list) == 44

    lspci_obj = LsPci(context_wrap(LSPCI_DRIVER_DETAILS_2))
    assert len(lspci_obj.data) == 4
    dev_info = lspci_obj.pci_dev_details('04:00.0')
    assert len(dev_info) == 2
    assert dev_info['Slot'] == '04:00.0'
    assert 'Kernel driver in use' not in dev_info
    assert len(lspci_obj.pci_dev_list) == 4

    lspci_obj = LsPci(context_wrap(LSPCI_DRIVER_DETAILS_3))
    assert len(lspci_obj.data) == 0
    assert len(lspci_obj.pci_dev_list) == 0

    output = LsPci(context_wrap(LSPCI_OUTPUT_WITH_BAD_LINES))
    assert len(output.data) == 1
    assert len(output.pci_dev_list) == 1


def test_lspci_vmmkn():
    lspci_vmmkn = LsPciVmmkn(context_wrap(LSPCI_VMMKN))
    assert sorted(lspci_vmmkn.pci_dev_list) == ['00:00.0', '00:01.0', '00:01.1', '00:03.0']
    assert lspci_vmmkn[0].get('Driver') is None
    assert lspci_vmmkn[0].get('Slot') == '00:00.0'
    assert lspci_vmmkn[1].get('Vendor') == '8086'
    assert lspci_vmmkn[1].get('Slot') == '00:01.0'
    assert lspci_vmmkn[1].get('Device') == '7010'
    assert lspci_vmmkn[2].get('Slot') == '00:01.1'
    assert lspci_vmmkn[2].get('SVendor') == '1af4'
    assert lspci_vmmkn[3].get('SDevice') == '0001'
    assert lspci_vmmkn[3].get('Slot') == '00:03.0'
    assert lspci_vmmkn[-1].get('Driver') == 'virtio-pci'
    assert sorted(lspci_vmmkn[1].get('Module')) == sorted(['ata_piix', 'ata_generic'])
    assert lspci_vmmkn[-1].get('Module') is None


def test_lspci_vmmkn_ab():
    with pytest.raises(SkipComponent):
        LsPciVmmkn(context_wrap(''))

    with pytest.raises(SkipComponent):
        LsPciVmmkn(context_wrap(' \n '.splitlines()))


def test_doc_examples():
    env = {
            'lspci': LsPci(context_wrap(LSPCI_DRIVER_DOC)),
            'lspci_vmmkn': LsPciVmmkn(context_wrap(LSPCI_VMMKN))
          }
    failed, total = doctest.testmod(lspci, globs=env)
    assert failed == 0
