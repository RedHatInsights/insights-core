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
OpenvSwitchOtherConfig - command ``ovs-vsctl -t 5 get Open_vSwitch . other_config``
===================================================================================

Class OpenvSwitchOtherConfig process the output of the following OpenvSwitch command:

ovs-vsctl -t 5 get Open_vSwitch . other_config


Sample input::

    {dpdk-init="true", dpdk-lcore-mask="30000003000", dpdk-socket-mem="4096,4096", pmd-cpu-mask="30000003000"}

Examples:

    >>> type(ovs_other_conf)
    <class 'insights.parsers.openvswitch_other_config.OpenvSwitchOtherConfig'>
    >>> ovs_other_conf.get("dpdk-init")
    true
    >>> ovs_other_conf["dpdk-lcore-mask"]
    30000003000
    >>> dpdk-socket-mem in ovs_other_conf
    True

"""

from .. import parser, LegacyItemAccess, CommandParser
from insights.specs import Specs
from . import optlist_to_dict


@parser(Specs.openvswitch_other_config)
class OpenvSwitchOtherConfig(LegacyItemAccess, CommandParser):
    """Parses output of the ovs-vsctl -t 5 get Open_vSwitch . other_config command"""

    def parse_content(self, content):
        self.data = {}
        one_line_content = ''.join(content).strip()
        if one_line_content.startswith("{"):
            new_line = one_line_content.strip("{}")
            if new_line:
                self.data = optlist_to_dict(new_line, opt_sep=", ", strip_quotes=True)
