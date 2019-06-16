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
OVSappctlFdbShowBridge - command ``/usr/bin/ovs-appctl fdb/show [bridge-name]``
===============================================================================

This module provides class ``OVSappctlFdbShowBridgeCount`` to parse the
output of command ``/usr/bin/ovs-appctl fdb/show [bridge-name]``.

Sample command output::

    port VLAN  MAC Age
    6       1 MAC1 118
    3       0 MAC2 24
"""

from insights import CommandParser, LegacyItemAccess, parser
from insights.parsers import SkipException
from insights.specs import Specs


@parser(Specs.ovs_appctl_fdb_show_bridge)
class OVSappctlFdbShowBridge(CommandParser, LegacyItemAccess):
    """
       This class provides processing for the output of the command
       ``/usr/bin/ovs-appctl fdb/show [bridge-name]``.

       Sample content collected by insights-client::

           port  VLAN  MAC                Age
              6    29  aa:bb:cc:dd:ee:ff  270
              3    27  gg:hh:ii:jj:kk:ll  266
              1   100  mm:nn:oo:pp:qq:rr  263

       Sample parsed output::

           {
               'br-int': [
                             {'port': '6', 'VLAN': '29', 'MAC': 'aa:bb:cc:dd:ee:ff', 'Age': '270'},
                             {'port': '3', 'VLAN': '27', 'MAC': 'gg:hh:ii:jj:kk:ll', 'Age': '266'},
                             {'port': '1', 'VLAN': '100', 'MAC': 'mm:nn:oo:pp:qq:rr', 'Age': '263'}
                         ]
           }

       Attributes:
           data (dict): A dictionary where each element contains the bridge-name
                        as key and list of dictionary elements having MAC info as
                        value.

       Raises:
           SkipException: When the file is empty or data is not present for a bridge.

       Examples:

            >>> len(data["br_tun"])
            2
            >>> data.get("br_tun")[1]["MAC"] == "gg:hh:ii:jj:kk:ll"
            True
            >>> int(data["br_tun"][0]["port"])
            7
    """

    def parse_content(self, content):
        if len(content) == 0:
            raise SkipException("Empty file")

        self.data = {}
        # Extract the bridge name
        bridge_name = self.file_path.split("ovs-appctl_fdb.show_")[-1]

        header = content[0].split()
        self.data[bridge_name] = [dict(zip(header, entry.split(None, len(header)))) for entry in content[1:]]
        if not self.data[bridge_name]:
            raise SkipException("No data present for {0}".format(bridge_name))
