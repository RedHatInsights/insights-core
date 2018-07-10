"""
OpenShiftHosts - file ``/root/.config/openshift/hosts``
========================================================

OpenShiftHosts file is /root/.config/openshift/hosts which
records nodes information. While installing openshift cluster
, this installation process would read this file, and install
relative rpms on every node according to the configuration.
"""


from .. import parser, Parser, get_active_lines, LegacyItemAccess
from insights.parsers import ParseException
from insights.specs import Specs
from insights.core.filters import add_filter

add_filter(Specs.openshift_hosts, "[")


@parser(Specs.openshift_hosts)
class OpenShiftHosts(Parser, LegacyItemAccess):
    """
    Class ``OpenShiftHosts`` parses the content of the ``/root/.config/openshift/hosts``` file.
    A small sample of the content of this file looks like::

        [OSEv3:children]
        nodes
        nfs
        masters
        etcd
        [OSEv3:vars]
        openshift_master_cluster_public_hostname=None
        ansible_ssh_user=root
        openshift_master_cluster_hostname=None
        openshift_hostname_check=false
        deployment_type=openshift-enterprise
        [nodes]
        master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com openshift_schedulable=False ansible_connection=local
        node1.ose35.com  openshift_public_ip=192.66.208.169 openshift_ip=192.66.208.169 openshift_public_hostname=node1.ose35.com openshift_hostname=node1.ose35.com connect_to=node1.ose35.com openshift_node_labels="{'region': 'infra'}" openshift_schedulable=True
        node2.ose35.com  openshift_public_ip=192.66.208.170 openshift_ip=192.66.208.170 openshift_public_hostname=node2.ose35.com openshift_hostname=node2.ose35.com connect_to=node2.ose35.com openshift_node_labels="{'region': 'infra'}" openshift_schedulable=True
        [nfs]
        master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com ansible_connection=local
        [masters]
        master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com ansible_connection=local
        [etcd]
        master.ose35.com  openshift_public_ip=192.66.208.202 openshift_ip=192.66.208.202 openshift_public_hostname=master.ose35.com openshift_hostname=master.ose35.com connect_to=master.ose35.com ansible_connection=local

    Examples:
        >>> type(host_info)
        <class 'insights.parsers.openshift_hosts.OpenShiftHosts'>
        >>> host_info["OSEv3:children"]
        ["nodes","nfs","masters","etcd"]
        >>> host_info["nodes"]["master.ose35.com"]["openshift_public_ip"]
        "192.66.208.202"
        >>> host_info["nodes"]["master.ose35.com"]["openshift_node_labels"]
        "{'region': 'infra'}"
        >>> host_info.has_node("node1.ose35.com")
        True
        >>> host_info.has_var("openshift_use_crio")
        False

    """

    def parse_content(self, content):
        dict_all = {}
        sub_section = ""
        for line in get_active_lines(content):
            if line.startswith("[") and line.endswith("]"):
                sub_section = line[1:-1].strip()
                if "OSEv3:children" in sub_section:
                    dict_all[sub_section] = []
                else:
                    dict_all[sub_section] = {}
                continue
            else:
                # Parser section [OSEv3:children]
                if "OSEv3:children" in sub_section:
                    dict_all[sub_section].append(line)
                # Parser section [OSEv3:vars]
                elif "OSEv3:vars" in sub_section:
                    key, value = line.split("=")
                    dict_all[sub_section][key.strip()] = value.strip()
                else:
                    nodename, nodeinfo = line.split(" ", 1)
                    dict_all[sub_section][nodename] = {}
                    splitwithsqual = nodeinfo.split("=")
                    keys = [splitwithsqual[0].strip()]
                    values = []
                    for item in splitwithsqual[1:-1]:
                        value, key = item.rsplit(" ", 1)
                        keys.append(key.strip())
                        # There is key-value like "openshift_node_labels="{'region': 'infra','zone': 'default'}"",
                        # convert the value as dict.
                        if "{" and "}" in value:
                            subkeyvalue = value[2:-2].split(",")
                            subdict = {}
                            for subitem in subkeyvalue:
                                subkey, subvalue = subitem.split(":")
                                subdict[subkey.strip()[1:-1]] = subvalue.strip()[1:-1]
                            values.append(subdict)
                        else:
                            values.append(value.strip())
                    values.append(splitwithsqual[-1].strip())
                    if len(keys) != len(values):
                        raise ParseException("Wrong Configuration")
                    for i in range(len(keys)):
                        dict_all[sub_section][nodename][keys[i]] = values[i]
        self.data = dict_all

    def has_var(self, var):
        """
        Indicate whether the named var is present in the configuration.
        Return True if the given var is present, and False if not present.
        """
        return "OSEv3:vars" in self.data and var in self.data["OSEv3:vars"]

    def has_node(self, node):
        """
        Indicate whether the named node is present in the configuration.
        Return True if the given node name is present, and False if not present.
        """
        return "nodes" in self.data and node in self.data["nodes"]

    def has_node_type(self, node_type):
        """
        Indicate whether the named node type is present in the configuration.
        Return True if the given node type is present, and False if not present.
        """
        return "OSEv3:children" in self.data and node_type in self.data["OSEv3:children"]
