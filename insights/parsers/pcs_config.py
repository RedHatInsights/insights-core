"""
PCSConfig - command ``pcs config``
==================================

This module provides class ``PCSConfig`` for parsing output of ``pcs config`` command.
Typical ``/usr/sbin/pcs config`` output looks something like:

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
Methods ``get_resources_clones()`` and ``get_resources_groups()`` parse ``Resources`` part of the output in more
convenient way. ``Resources`` contains two main subcategories: Clone and Group. ``get_resources_clones()`` provides
dictionary of clones. Each Clone then contains list of associated lines. ``get_resources_groups()`` works the same
way for the Groups.


Examples:

    >>> from insights.parsers.pcs_config import PCSConfig
    >>> from insights.tests import context_wrap
    >>>
    >>> pcs_config_output = '''
    ... Cluster Name: cluster-1
    ... Corosync Nodes:
    ...  node-1 node-2
    ... Pacemaker Nodes:
    ...  node-1 node-2
    ...
    ... Resources:
    ...  Clone: clone-1
    ...  Meta Attrs: interleave=true ordered=true
    ...  Resource: res-1 (class=ocf provider=pacemaker type=controld)
    ...  Operations: start interval=0s timeout=90 (dlm-start-interval-0s)
    ...              stop interval=0s timeout=100 (dlm-stop-interval-0s)
    ...              monitor interval=30s on-fail=fence (dlm-monitor-interval-30s)
    ...
    ... Stonith Devices:
    ... Fencing Levels:
    ...
    ... Location Constraints:
    ...  Resource: fence-1
    ...  Resource: res-1
    ... Ordering Constraints:
    ... Colocation Constraints:
    ...
    ... Resources Defaults:
    ...  No defaults set
    ... Operations Defaults:
    ...  No defaults set
    ...
    ... Cluster Properties:
    ...  cluster-infrastructure: corosync
    ...  cluster-name: cluster-1
    ... '''.strip()
    >>>
    >>> shared = {PCSConfig: PCSConfig(context_wrap(pcs_config_output))}
    >>> pcs_config = shared[PCSConfig]
    >>> pcs_config.get("Corosync Nodes")
    ['node-1', 'node-2']
    >>> pcs_config.get("Cluster Properties")
    ['cluster-infrastructure: corosync', 'cluster-name: cluster-1']
    >>> pcs_config.get_resources_clones()
    {'clone-1': ['Meta Attrs: interleave=true ordered=true', 'Resource: res-1 (class=ocf provider=pacemaker type=controld)', 'Operations: start interval=0s timeout=90 (dlm-start-interval-0s)', 'stop interval=0s timeout=100 (dlm-stop-interval-0s)', 'monitor interval=30s on-fail=fence (dlm-monitor-interval-30s)', '']}
    
"""


from .. import parser, CommandParser
from insights.specs import Specs
import sys


@parser(Specs.pcs_config)
class PCSConfig(CommandParser):
    """Class to process the output of ``pcs config`` command.

    Attributes:
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
    Methods:
        get_resources_clones(self) (dict): Returns a dictionary of ``Clones`` in ``Resources`` keyed with their name.
            the form::
            { 
                "clone-1": [
                    "Meta Attrs: interleave=true ordered=true",
                    "Resource: res-1 (class=ocf provider=pacemaker type=controld)"
                ],
                "clone-1": [
                    "Meta Attrs: interleave=true ordered=true",
                    "Resource: res-1 (class=ocf provider=pacemaker type=controld)"
                ]
            }

        get_resources_groups(self) (dict): Returns a dictionary of ``Gropus`` in ``Resources`` keyed with their name.
            the form::
            {
                "svcexzpr": [
                    "Resource: ip_exzpr (class=ocf provider=heartbeat type=IPaddr2)",
                    "Attributes: ip=10.198.107.14 cidr_netmask=32",
                    "Resource: fs_exzpr (class=ocf provider=heartbeat type=Filesystem)",
                    "Attributes: device=/dev/vg_exzpr/lv_exzpr directory=/exzpr fstype=xfs run_fsck=yes fast_stop=yes"
                ]
            }
    """

    def parse_content(self, content):
        self.data = {}
        dc_key = ""
        list_data = []
        skip_lines = 0
        config_tuple = ("Resources", "Stonith Devices", "Fencing Levels", "Location Constraints", "Ordering Constraints",
                        "Colocation Constraints", "Ticket Constraints", "Alerts", "Resources Defaults",
                        "Operations Defaults" ,"Cluster Properties" ,"Quorum")
        for i, line in enumerate(content):
            if skip_lines > 0:
                skip_lines -= 1
                continue
            if line.startswith("Cluster Name:"):
                self.data["Cluster Name"] = line.split("Cluster Name:")[-1].lstrip()
                continue
            if line.startswith("Corosync Nodes:"):
                self.data["Corosync Nodes"] = content[i+1].split()
                skip_lines = 1
                continue
            if line.startswith("Pacemaker Nodes:"):
                self.data["Pacemaker Nodes"] = content[i+1].split()
                skip_lines = 1
                continue
            if line == "":
                if not dc_key == "":
                    self.data[dc_key] = list_data
                    list_data = []
                    dc_key = ""
                continue
            if line.startswith(config_tuple) and (len(line) - len(line.lstrip()) == 0):
                if not dc_key == "":
                    self.data[dc_key] = list_data
                    list_data = []
                dc_key = line.split(":")[0]
                continue
            list_data.append(line.lstrip())
        if not dc_key == "" and not dc_key in self.data.keys():
            self.data[dc_key] = list_data


    def get(self, key):
        return self.data.get(key)


    def get_resources_clones(self):
        clones = {}
        name = ""
        in_clone = 0
        for line in self.data.get("Resources"):
            if line.startswith("Clone:"):
                name = line.split(":")[-1].strip()
                clones[name] = []
                in_clone = 1
                continue
            if in_clone == 0:
                continue
            if line.startswith("Group:"):
                in_clone = 0
                name = ""
                continue
            clones[name].append(line)
        return clones


    def get_resources_groups(self):
        groups = {}
        name = ""
        in_group = 0
        for line in self.data.get("Resources"):
            if line.startswith("Group:"):
                name = line.split(":")[-1].strip()
                groups[name] = []
                in_group = 1
                continue
            if in_group == 0:
                continue
            if line.startswith("Clone:"):
                in_group =  0
                name = ""
                continue
            groups[name].append(line)
        return groups
