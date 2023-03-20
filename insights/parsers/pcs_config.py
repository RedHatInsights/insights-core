"""
PCSConfig - command ``pcs config``
==================================

This module provides class ``PCSConfig`` for parsing output of ``pcs config`` command.

Typical ``/usr/sbin/pcs config`` output looks something like::

    Cluster Name: cluster-1
    Corosync Nodes:
     node-1 node-2
    Pacemaker Nodes:
     node-1 node-2

    Resources:
     Clone: clone-1
     Meta Attrs: interleave=true ordered=true
     Resource: res-1 (class=ocf provider=pacemaker type=controld)
      Operations: start interval=0s timeout=90 (dlm-start-interval-0s)
                  stop interval=0s timeout=100 (dlm-stop-interval-0s)
                  monitor interval=30s on-fail=fence (dlm-monitor-interval-30s)
     Group: grp-1
     Resource: res-1 (class=ocf provider=heartbeat type=IPaddr2)
      Attributes: ip=10.0.0.1 cidr_netmask=32
      Operations: monitor interval=120s (ip_monitor-interval-120s)
                  start interval=0s timeout=20s (ip_-start-interval-0s)
                  stop interval=0s timeout=20s (ip_-stop-interval-0s)

    Stonith Devices:
    Fencing Levels:

    Location Constraints:
    Resource: fence-1
        Disabled on: res-mgt (score:-INFINITY) (id:location-fence-1--INFINITY)
    Resource: res-1
        Enabled on: res-mcast (score:INFINITY) (role: Started) (id:cli-prefer-res)
    Ordering Constraints:
    Colocation Constraints:

    Resources Defaults:
     resource-stickiness: 100
     migration-threshold: 3
    Operations Defaults:
     No defaults set

    Cluster Properties:
     cluster-infrastructure: corosync
     cluster-name: cluster-1
     dc-version: 1.1.13-10.el7_2.4-44eb2dd
     have-watchdog: false
     no-quorum-policy: ignore
     stonith-enable: true
     stonith-enabled: false

The class provides attribute ``data`` as dictionary with lines parsed line by line based on keys, which are
the key words of the output.
Information in keys ``Corosync Nodes`` and ``Pacemaker Nodes`` is parsed in one line.
The get method ``get(str)`` provides lines from ``data`` based on given key.

Examples:
    >>> pcs_config.get("Cluster Name")
    'cluster-1'
    >>> pcs_config.get("Corosync Nodes")
    ['node-1', 'node-2']
    >>> pcs_config.get("Cluster Properties")
    ['cluster-infrastructure: corosync', 'cluster-name: cluster-1', 'dc-version: 1.1.13-10.el7_2.4-44eb2dd', 'have-watchdog: false', 'no-quorum-policy: ignore', 'stonith-enable: true', 'stonith-enabled: false']
    >>> pcs_config.get("Colocation Constraints")
    ['clone-1 with clone-x (score:INFINITY) (id:clone-INFINITY)', 'clone-2 with clone-x (score:INFINITY) (id:clone-INFINITY)']
    >>> 'have-watchdog' in pcs_config.cluster_properties
    True
    >>> pcs_config.cluster_properties.get('have-watchdog')
    'false'
"""


from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.pcs_config)
class PCSConfig(CommandParser):
    """Class to process the output of ``pcs config`` command.

    Attributes:
        cluster_properties (dict): A dictionary containing all cluster properties key, value
        data (dict): A dictionary containing all line. Keys sorted based on keywords of the output.
            the form::

                {
                    "Cluster Name": "cluster-1",
                    "Corosync Nodes": [
                        "node-1",
                        "node-2"
                    ],
                    "Pacemaker Nodes": [
                        "node-1",
                        "node-2"
                    ],
                    "Resources": [
                        "Clone: clone-1",
                        "Meta Attrs: interleave=true ordered=true",
                        "Resource: res-1 (class=ocf provider=pacemaker type=controld)",
                        "Operations: start interval=0s timeout=90 (dlm-start-interval-0s)",
                        "stop interval=0s timeout=100 (dlm-stop-interval-0s)",
                        "monitor interval=30s on-fail=fence (dlm-monitor-interval-30s)"
                    ],
                    "Cluster Properties": [
                        "cluster-infrastructure: corosync",
                        "cluster-name: cluster-1"
                    ]
                }
    """

    def parse_content(self, content):
        self.data = {}
        self.cluster_properties = {}
        dc_key = ""
        list_data = []
        in_line_tuple = ("Corosync Nodes", "Pacemaker Nodes")
        for i, line in enumerate(content):
            if line.startswith("Cluster Name:"):
                self.data["Cluster Name"] = line.split("Cluster Name:")[-1].lstrip()
                continue
            if line == "":
                if not dc_key == "":
                    self.data[dc_key] = list_data
                    list_data = []
                    dc_key = ""
                continue
            if (len(line) - line.find(":") == 1) and (len(line) - len(line.lstrip()) == 0):
                if not dc_key == "":
                    self.data[dc_key] = list_data
                    list_data = []
                dc_key = line.split(":")[0]
                continue
            list_data.append(line.lstrip())
            # build cluster properties dict
            if dc_key == 'Cluster Properties':
                cp_key, _, cp_value = line.partition(":")
                self.cluster_properties[cp_key.strip()] = cp_value.strip()
        if not dc_key == "" and dc_key not in self.data.keys():
            self.data[dc_key] = list_data
        for in_line in in_line_tuple:
            if isinstance(self.data.get(in_line), list) and self.data[in_line]:
                self.data[in_line] = self.data[in_line][0].split()

    def get(self, key):
        return self.data.get(key)
