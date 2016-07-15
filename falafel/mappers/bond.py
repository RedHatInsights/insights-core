from falafel.core.plugins import mapper
from falafel.core import MapperOutput

class BondInfo(MapperOutput):

    def __init__(self, data):
        self.data = data.content
        self.path = data.path

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in lspci output.
        """
        return any(s in line for line in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list
        """
        return [line for line in self.data if s in line]

    def bond_name(self):
        """
        return a dict contains the name of bond interface.
        """
        info_dict = {}
        info_dict["iface"] = self.path.split('/')[-1]
        return info_dict


@mapper('bond')
def bondinfo(context):
    """
    Returns an object of BondInfo.
    """
    return BondInfo(context)
