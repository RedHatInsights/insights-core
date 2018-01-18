"""
OpenvSwitchOtherConfig - command ``ovs-vsctl -t 5 get Open_vSwitch . other_config``
===================================================================================

Class OpenvSwitchOtherConfig process the output of the following OpenvSwitch command:

ovs-vsctl -t 5 get Open_vSwitch . other_config


Sample input::

    {dpdk-init="true", dpdk-lcore-mask="30000003000", dpdk-socket-mem="4096,4096", pmd-cpu-mask="30000003000"}

Examples:

    >>> ovs_other_conf = shared[OpenvSwitchOtherConfig]
    >>> ovs_other_conf.get("dpdk-init")
    true
    >>> ovs_other_conf["dpdk-lcore-mask"]
    "30000003000"
    >>> dpdk-socket-mem in ovs_other_conf
    True

"""

from .. import Parser, parser, LegacyItemAccess
from . import optlist_to_dict


@parser("openvswitch_other_config")
class OpenvSwitchOtherConfig(LegacyItemAccess, Parser):
    """Parses output of the ``ovs-vsctl -t 5 get Open_vSwitch . other_config`` command."""
    def parse_content(self, content):
        self.data = {}
        one_line_content = ''.join(content).strip()
        if one_line_content.startswith("{"):
            new_line = one_line_content.strip("{}")
            if new_line:
                self.data = optlist_to_dict(new_line, opt_sep=", ", strip_quotes=True)
