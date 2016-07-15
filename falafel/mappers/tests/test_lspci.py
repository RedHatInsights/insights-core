from falafel.mappers import lspci
from falafel.tests import context_wrap


LSPCI_0 = """
00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)
00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
0d:00.0 System peripheral: Ricoh Co Ltd PCIe SDXC/MMC Host Controller (rev 07)
""".strip()



def test_lspci():
    lspci_0 = lspci.lspci(context_wrap(LSPCI_0))
    assert lspci_0.get("Intel Corporation") == \
            ['00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)',
            '00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)',
            '03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)']
    assert len(lspci_0.get("Network controller")) == 1
    assert "Centrino Advanced-N 6205" in lspci_0
    assert "0d:00.0" in lspci_0
