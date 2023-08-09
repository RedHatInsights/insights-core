"""
nmcli_dev_show command
======================
As there are three different file paths in different sos packages,
create this combiner to fix this issue.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.nmcli import NmcliDevShow, NmcliDevShowSos


@combiner([NmcliDevShow, NmcliDevShowSos])
class AllNmcliDevShow(dict):
    """
    Combiner to combine return values from parser NmcliDevShow into one dict

    Examples:
        >>> allnmclidevshow['eth0']['TYPE']
        'ethernet'
        >>> allnmclidevshow.connected_devices
        ['eth0']
    """

    def __init__(self, nmclidevshow, nmclidevshowsos):
        data = {}
        self._con_dev = []

        if nmclidevshow:
            data.update(nmclidevshow)
            self._con_dev = nmclidevshow.connected_devices
        elif nmclidevshowsos:
            for item in nmclidevshowsos:
                data.update(item)
                self._con_dev.extend(item.connected_devices)

        if not data:
            raise SkipComponent()

        super(AllNmcliDevShow, self).__init__()
        self.update(data)

    @property
    def connected_devices(self):
        """(list): The list of devices who's state is connected and managed by NetworkManager"""
        return self._con_dev

    @property
    def data(self):
        """(dict): Dict with the device name as the key and NmcliDevShow details as the value."""
        return self
