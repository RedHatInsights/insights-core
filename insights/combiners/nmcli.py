"""
nmcli_dev_show command
======================
As there are three different file paths in different sos packages,
create this combiner to fix this issue.
"""

from insights.core.plugins import combiner
from insights.parsers.nmcli import NmcliDevShow, NmcliDevShowSos


@combiner(optional=[NmcliDevShow, NmcliDevShowSos])
class Allnmclidevshow(object):
    """
    Combiner method to combine return value from parser NmcliDevShow into one dict

    Returns:
        data: interface info from nmcli dev shows commnand

    Examples:
        >>> allnmclidevshow.data['eth0']['TYPE']
        'ethernet'
        >>> allnmclidevshow.connected_devices
        ['eth0']
    """

    def __init__(self, nmclidevshow, nmclidevshowsos):
        self.data = {}

        if nmclidevshow:
            self.data.update(nmclidevshow.data)
        if nmclidevshowsos:
            for item in nmclidevshowsos:
                self.data.update(item.data)

        super(Allnmclidevshow, self).__init__()

    @property
    def connected_devices(self):
        """(list): The list of devices who's state is connected and managed by NetworkManager"""
        con_dev = []
        for key in self.data:
            if 'STATE' in self.data[key] and self.data[key]['STATE'] == 'connected':
                con_dev.append(key)
        return con_dev
