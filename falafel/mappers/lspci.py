from falafel.core.plugins import mapper
from falafel.core import MapperOutput


class LsPCI(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in lspci output
        """
        return any(s in line for line in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list
        """
        return [line for line in self.data if s in line]


@mapper('lspci')
def lspci(context):
    """
    ----------------- Output sample of command lspci --------------------------
    00:00.0 Host bridge: Intel Corporation 2nd Generation Core Processor Family DRAM Controller (rev 09)
    00:02.0 VGA compatible controller: Intel Corporation 2nd Generation Core Processor Family Integrated Graphics Controller (rev 09)
    03:00.0 Network controller: Intel Corporation Centrino Advanced-N 6205 [Taylor Peak] (rev 34)
    0d:00.0 System peripheral: Ricoh Co Ltd PCIe SDXC/MMC Host Controller (rev 07)
    ----------------- Output sample of command lspci --------------------------

    """
    return LsPCI(context.content)
