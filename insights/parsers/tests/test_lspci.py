from insights.parsers.lspci import LsPci
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


def test_lspci():
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
