"""
Ansible Hosts file ``/etc/ansible/hosts``
=========================================

A /etc/ansible/hosts file consists of host groups and hosts within those
groups. This file is Ansible's inventory file for the playbook used to
install OpenShift Container Platform. The inventory file describes the
configuration for your OpenShift Container Platform cluster.

"""

from .. import parser, Parser, LegacyItemAccess
from insights.specs import Specs
from insights.core.filters import add_filter

add_filter(Specs.ansible_hosts, "[")


@parser(Specs.ansible_hosts)
class AnsibleHosts(Parser, LegacyItemAccess):
    """
    It parse the content of the file ``/etc/ansible/hosts`` file.
    Sample of the content of this file::

        mail.example.com

        [webservers]
        foo.example.com
        bar.example.com

        [raleigh]
        host2
        host3

        mail.example.com

        [southeast:children]
        atlanta
        raleigh

        ansible_become=true

        [targets]
        localhost              ansible_connection=local
        other1.example.com     ansible_connection=ssh        ansible_user=mpdehaan
        other2.example.com     ansible_connection=ssh        ansible_user=mdehaan

        [atlanta]
        host1
        host2

        [atlanta:vars]
        ntp_server=ntp.atlanta.example.com
        proxy=proxy.atlanta.example.com

    Examples:
        >>> type(hosts_info)
        <class 'insights.parsers.ansible_hosts.AnsibleHosts'>
        >>> 'host1' in hosts_info["raleigh"]
        False
        >>> 'bar.example.com' in hosts_info["webservers"]
        True
        >>> hosts_info["southeast:children"]
        ['atlanta', 'raleigh']
        >>> hosts_info["targets"]["localhost"]["ansible_connection"]
        'local'
        >>> hosts_info.has_var("ansible_become")
        True
        >>> hosts_info.has_host("any.node.com")
        False
        >>> hosts_info.has_host("mail.example.com")
        True

    """

    def parse_content(self, content):
        dict_all = {}
        dict_all["global-vars"] = {}
        dict_all["ungrouped-hosts"] = {}
        section = ""

        for line in content:
            line = line.strip()
            if line.startswith("#"):
                continue

            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()

                if section.endswith(":vars"):
                    dict_all[section] = {}
                elif section.endswith(":children"):
                    dict_all[section] = []
                else:
                    dict_all[section] = {}
                continue

            # Get global variables and ungrouped hosts
            elif (not section) and (line):
                space_separated_line = line.split(" ", 1)
                if len(space_separated_line) == 1:
                    if space_separated_line[0].find("=") == -1:
                        dict_all["ungrouped-hosts"][space_separated_line[0]] = {}
                    else:
                        key, value = line.split("=")
                        dict_all["global-vars"][key.strip()] = value.strip()
                else:
                    host, host_vars = line.split(" ", 1)
                    dict_all["ungrouped-hosts"][host.strip()] = {}
                    splitwithequal = host_vars.split("=")
                    keys = [splitwithequal[0].strip()]
                    values = []
                    for item in splitwithequal[1:-1]:
                        value, key = item.rsplit(" ", 1)
                        keys.append(key.strip())
                        values.append(value.strip())
                    values.append(splitwithequal[-1].strip())

                    for i in range(len(keys)):
                        dict_all["ungrouped-hosts"][host][keys[i]] = values[i]

            elif section:
                if not line:
                    section = ""
                    continue

                if section.endswith(":children"):
                    dict_all[section].append(line)

                elif section.endswith(":vars"):
                    key, value = line.split("=")
                    dict_all[section][key.strip()] = value.strip()
                else:
                    if len(line.split(" ")) == 1:
                        dict_all[section][line] = {}
                    else:
                        host, host_vars = line.split(" ", 1)
                        dict_all[section][host.strip()] = {}
                        splitwithequal = host_vars.split("=")
                        keys = [splitwithequal[0].strip()]
                        values = []
                        for item in splitwithequal[1:-1]:
                            value, key = item.rsplit(" ", 1)
                            keys.append(key.strip())
                            values.append(value.strip())
                        values.append(splitwithequal[-1].strip())

                        for i in range(len(keys)):
                            dict_all[section][host][keys[i]] = values[i]

        self.data = dict_all

    def has_var(self, var):
        """
        Indicate whether the named var is present in configuration.

        :param var: Global variable
        :return: True if the given var is present and False if not present
        """
        return ("global-vars" in self.data) and (var in self.data["global-vars"])

    def has_host(self, host):
        """
        Indicate whether the host is present in the configuration.

        :param host: Grouped or ungrouped host
        :return: True if the given host is present, anf False if not present.
        """
        present_in_ungrouped = "ungrouped-hosts" in self.data and \
            host in self.data["ungrouped-hosts"].keys()

        present_in_hosts_group = False
        for group in self.data:
            if group.endswith(":vars") or group.endswith(":children"):
                continue
            elif host in self.data[group].keys():
                present_in_hosts_group = True

        return present_in_ungrouped or present_in_hosts_group
