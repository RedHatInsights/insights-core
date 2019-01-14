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
"""

from insights import parser, CommandParser
from insights.parsers import ParseException, parse_fixed_table
from insights.specs import Specs


@parser(Specs.oc_get_clusterrole_with_config)
class OcGetClusterRoleWithConfig(CommandParser):
    """
    Class to parse ``oc get clusterrole --config /etc/origin/master/admin.kubeconfig``

    A typical sample of the content of this file looks like::

        NAME
        admin
        asb-access
        asb-auth
        basic-user
        cluster-admin
        cluster-debugger
        cluster-reader
        cluster-status
        edit
        hawkular-metrics-admin
        management-infra-admin
        namespace-viewer
        registry-admin

    Examples:
        >>> type(oc_get_cluster_role_with_config)
        <class 'insights.parsers.openshift_get_with_config.OcGetClusterRoleWithConfig'>
        >>> oc_get_cluster_role_with_config[0]
        'admin'
    """

    def parse_content(self, content):
        if len(content) < 2 or content[0].strip() != "NAME":
            raise ParseException("invalid content: {0}".format(content) if content else 'empty file')
        self.data = list(map(lambda x: x.strip(), content[1:]))

    def __getitem__(self, item):
        return self.data[item]

    def __contains__(self, item):
        return item in self.data


@parser(Specs.oc_get_clusterrolebinding_with_config)
class OcGetClusterRoleBindingWithConfig(CommandParser):
    """
    Class to parse ``oc get clusterrolebinding --config /etc/origin/master/admin.kubeconfig``

    Attributes:
        data (list): List of dicts, each dict containing one row of the table
        rolebinding (dict): It is a dictionary in which the key is rolebinding name and the value is the role.

    A typical sample of the content of this file looks like::

        NAME                                                                  ROLE                                                                   USERS                            GROUPS                                         SERVICE ACCOUNTS                                                                   SUBJECTS
        admin                                                                 /admin                                                                                                                                                 openshift-infra/template-instance-controller
        admin-0                                                               /admin                                                                                                                                                 kube-service-catalog/default
        admin-1                                                               /admin                                                                                                                                                 openshift-ansible-service-broker/asb
        asb-access                                                            /asb-access                                                                                                                                            openshift-ansible-service-broker/asb-client
        asb-auth                                                              /asb-auth                                                                                                                                              openshift-ansible-service-broker/asb
        auth-delegator-openshift-template-service-broker                      /system:auth-delegator                                                                                                                                 openshift-template-service-broker/apiserver
        basic-users                                                           /basic-user                                                                                             system:authenticated
        cluster-admin                                                         /cluster-admin                                                                                          system:masters
        cluster-admin-0                                                       /cluster-admin                                                                                                                                         insights-scan/insights-scan

    Examples:
        >>> type(oc_get_clusterrolebinding_with_config)
        <class 'insights.parsers.openshift_get_with_config.OcGetClusterRoleBindingWithConfig'>
        >>> oc_get_clusterrolebinding_with_config.rolebinding["admin"]
        '/admin'
    """

    def parse_content(self, content):
        if len(content) < 2 or "NAME" not in content[0]:
            raise ParseException("invalid content: {0}".format(content) if content else 'empty file')

        self.data = parse_fixed_table(content, header_substitute=[('SERVICE ACCOUNTS', 'SERVICE_ACCOUNTS')])
        self.rolebinding = {}

        for rolebinding in self.data:
            rolebinding_name = rolebinding["NAME"].strip()
            rolebinding_role = rolebinding["ROLE"].strip()
            if rolebinding_name and rolebinding_role:
                self.rolebinding[rolebinding_name] = rolebinding_role
