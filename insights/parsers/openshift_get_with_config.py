"""
OpenShift Get commands with configuration file
==============================================

The commands set is similar to the ``oc get`` commands. It is used to display openshift resources.
It uses the master configuration file rather than the default configuration when communicated with the client API.
It makes sure this command will only be executed on the master node of an OpenShift cluster.
This command will also not include the commands which display large size outputs.

Parsers included in this module are:

OcGetClusterRoleWithConfig - command ``oc get clusterrole --config /etc/origin/master/admin.kubeconfig``
--------------------------------------------------------------------------------------------------------

OcGetClusterRoleBindingWithConfig - command ``oc get clusterrolebinding --config /etc/origin/master/admin.kubeconfig``
----------------------------------------------------------------------------------------------------------------------

Examples:
    >>> type(oc_get_cluster_role_with_config)
    <class 'insights.parsers.openshift_get_with_config.OcGetClusterRoleWithConfig'>
    >>> oc_get_cluster_role_with_config.role[0]
    'admin'
    >>> type(oc_get_clusterrolebinding_with_config)
    <class 'insights.parsers.openshift_get_with_config.OcGetClusterRoleBindingWithConfig'>
    >>> oc_get_clusterrolebinding_with_config.rolebinding["admin"]
    '/admin'
"""

from .. import parser, CommandParser
from . import ParseException
from insights.specs import Specs


@parser(Specs.oc_get_cluster_role_with_config)
class OcGetClusterRoleWithConfig(CommandParser):
    """Class to parse ``oc get clusterrole --config /etc/origin/master/admin.kubeconfig``"""

    def parse_content(self, content):
        if len(content) < 2 or content[0].strip() != "NAME":
            raise ParseException("Error: ", content if content else 'empty file')
        self.role = list(map(lambda x: x.strip(), content[1:]))


@parser(Specs.oc_get_clusterrolebinding_with_config)
class OcGetClusterRoleBindingWithConfig(CommandParser):
    """Class to parse ``oc get clusterrolebinding --config /etc/origin/master/admin.kubeconfig``"""

    def parse_content(self, content):
        self.rolebinding = {}
        if len(content) < 2 or "NAME" not in content[0]:
            raise ParseException("{0}: invalid content".format(self.__class__.__name__))

        for line in content[1:]:
            item_list = line.split()
            if '/' not in line or len(item_list) < 2:
                raise ParseException("{0}: invalid ROLE format".format(self.__class__.__name__))
            self.rolebinding[item_list[0]] = item_list[1]
