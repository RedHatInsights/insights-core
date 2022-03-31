"""
PCSStatus - command ``pcs status``
==================================

This module provides the classs ``PCSStatus`` which processes
``/usr/sbin/pcs status`` command output. Typical output of the ``pcs status``
command looks like::

    Cluster name: mycluster
    Last updated: Thu Dec  1 02:33:50 2016		Last change: Wed Aug  3 03:47:11 2016 by root via cibadmin on nodea.example.com
    Stack: corosync
    Current DC: nodea.example.com (version 1.1.13-10.el7-44eb2dd) - partition WITHOUT quorum
    3 nodes and 3 resources configured

    Online: [ nodea.example.com ]
    OFFLINE: [ nodeb.example.com nodec.example.com ]

    Full list of resources:
        myfence	(stonith:fence_xvm):	Stopped
        Resource Group: myweb
            webVIP	(ocf::heartbeat:IPaddr2):	Stopped
            webserver	(ocf::heartbeat:apache):	Stopped
    PCSD Status:
        nodea.example.com: Online
        nodeb.example.com: Offline
        nodec.example.com: Offline
    Daemon Status:
        corosync: active/enabled
        pacemaker: active/enabled
        pcsd: active/enabled

The class ``PCSStatus`` has one attribute ``nodes`` whick is a list containing all
node names that from ``PCSD Status`` section.


Examples:

    >>> pcsstatus_content = '''
    ... Cluster name: openstack
    ... Last updated: Fri Oct 14 15:45:32 2016
    ... Last change: Thu Oct 13 20:02:27 2016
    ... Stack: corosync
    ... Current DC: myhost15 (1) - partition with quorum
    ... Version: 1.1.12-a14efad
    ... 3 Nodes configured
    ... 143 Resources configured
    ... online: [ myhost15 myhost16 myhost17 ]
    ... Full list of resources:
    ... stonith-ipmilan-10.24.221.172	(stonith:fence_ipmilan):	Started myhost15
    ... stonith-ipmilan-10.24.221.171	(stonith:fence_ipmilan):	Started myhost16
    ... stonith-ipmilan-10.24.221.173	(stonith:fence_ipmilan):	Started myhost15
    ... PCSD Status:
    ...     myhost15: Online
    ...     myhost17: Online
    ...     myhost16: Online
    ... Daemon Status:
    ...    corosync: active/enabled
    ...    pacemaker: active/enabled
    ...    pcsd: active/enabled
    ... '''.strip()
    >>> from insights.tests import context_wrap
    >>> shared = {PCSStatus: PCSStatus(context_wrap(pcsstatus_content))}
    >>> pcsstatus_info = shared[PCSStatus]
    >>> pcsstatus_info.get("Cluster name")
    'openstack'
    >>> pcsstatus_info.get("Stack")
    'corosync'
    >>> pcsstatus_info.get("Nodes configured")
    '3'
    >>> pcsstatus_info.get("Resources configured")
    '143'
    >>> pcsstatus_info.nodes
    ['myhost15', 'myhost17', 'myhost16']
    >>> len(pcsstatus_info.get("Full list of resources"))
    3
"""
from insights import parser, CommandParser
from insights.specs import Specs


@parser(Specs.pcs_status)
class PCSStatus(CommandParser, dict):
    """Class to process the output of ``pcs status`` command.

    Sample Output::

        {
            "Resources configured": "143",
            "PCSD Status": [
                "myhost15: Online",
                "myhost17: Online",
                "myhost16: Online"
            ],
            "Current DC": "myhost15 (1) - partition with quorum",
            "Full list of resources": [
                "stonith-ipmilan-10.24.221.172\t(stonith:fence_ipmilan):\tStarted myhost15",
                "stonith-ipmilan-10.24.221.171\t(stonith:fence_ipmilan):\tStarted myhost16",
                "stonith-ipmilan-10.24.221.173\t(stonith:fence_ipmilan):\tStarted myhost15",
            ],
            "Daemon Status": [
                "corosync: active/enabled",
                "pacemaker: active/enabled",
                "pcsd: active/enabled"
            ],
            "Nodes configured": "3",
            "Online": "[ myhost15 myhost16 myhost17 ]",
            "Cluster name": "openstack",
            "Stack": "corosync"
        }

    Attributes:
        nodes (list): A list containing all node names according "PCSD Status" section
    """

    def parse_content(self, content):
        self.nodes = []
        self.bad_nodes = []
        # according this file  https://github.com/ClusterLabs/pacemaker/blob/d078ca4a9ac72fc96073a215da2eed48939536f5/tools/crm_mon.c
        key_oneline = (
            "Cluster name", "Stack", "Current DC", "Online", "RemoteOnline", "OFFLINE", "RemoteOFFLINE", "GuestOnline")
        key_nextline_titles = (
            "Full list of resources",
            "Full List of Resources",
            "Failed Actions",
            "Failed Resource Actions",
            "Failed Fencing Actions",
            "PCSD Status",
            "Daemon Status",
            "Migration Summary",
            "Fencing History",
            "Node List",
            "Node Attributes",
            "Tickets"
        )
        # pacemaker changes some prefix after version 1.0 and 2.0
        key_nextline_alias = {
            "Full List of Resources": "Full list of resources",
            "Failed Resource Actions": "Failed Actions",  # "Failed Actions" was renamed to "Failed Resource Actions" at https://github.com/ClusterLabs/pacemaker/pull/1521
        }
        key_nextline_start = 0
        multiple_lines = []
        for line in content:
            if line.startswith("WARNING:"):
                if "WARNING" in self:
                    self["WARNING"].append(line.strip())
                else:
                    self["WARNING"] = [line.strip()]
                continue
            if (line.startswith("RemoteNode") or line.startswith("GuestNode") or (line.startswith("Node") and not line.startswith('Node List'))):
                linesplit = line.split()
                bad_node = {}
                bad_node['name'] = linesplit[1][0:-1]
                bad_node['status'] = line.split(':')[1][1:]
                self.bad_nodes.append(bad_node)
            if line.startswith(key_nextline_titles):
                key_nextline_start = 1
                multiple_lines = []
                attr_name = line.split(":")[0].strip()
                self[key_nextline_alias.get(attr_name, attr_name)] = multiple_lines
                continue
            if key_nextline_start == 0:
                line = line.strip('* ')
                linesplit = line.split()
                if line.startswith(key_oneline):
                    key, value = line.split(":", 1)
                    self[key.strip()] = value.strip()
                elif "nodes configured" in line.lower():
                    self["Nodes configured"] = linesplit[0]
                elif any(item in line.lower() for item in ["resources configured", "resource instance configured", "resource instances configured"]):
                    if "and" in line:  # 3 nodes and 3 resources configured
                        self['Nodes configured'] = linesplit[0]
                        self["Resources configured"] = linesplit[3]
                    else:
                        self["Resources configured"] = linesplit[0]
            else:  # key_nextline_start > 0
                if line.strip():
                    multiple_lines.append(line.strip())
        pcsd_status = self.get("PCSD Status")
        if pcsd_status:
            # According "PCSD Status" to get node list
            for line in pcsd_status:
                if line.count(':') > 1:
                    self.nodes.extend([item.split(':')[0] for item in line.split() if ':' in item])
                else:
                    self.nodes.append(line.split(":")[0].strip())

    @property
    def data(self):
        # to keep compatibility with old usage, please use itselt directly.
        return self
