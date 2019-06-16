#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
nmcli_dev_show command
======================
As there are three different file paths in different sos packages,
create this combiner to fix this issue.
"""

from insights.core.plugins import combiner
from insights.parsers.nmcli import NmcliDevShow, NmcliDevShowSos, SkipException


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
        self.data = {}
        self._con_dev = []

        if nmclidevshow:
            self.data.update(nmclidevshow.data)
            self._con_dev = nmclidevshow.connected_devices
        elif nmclidevshowsos:
            for item in nmclidevshowsos:
                self.data.update(item.data)
                self._con_dev.extend(item.connected_devices)

        if not self.data:
            raise SkipException()

        super(AllNmcliDevShow, self).__init__()
        self.update(self.data)

    @property
    def connected_devices(self):
        """(list): The list of devices who's state is connected and managed by NetworkManager"""
        return self._con_dev
