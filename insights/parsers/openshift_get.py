"""
OpenShift Get commands
======================

``oc get`` command is from openshift used to list the usage info - e.g.
pods info, dc info, services info, etc.  This shared parser is used to parse
``oc get XX --all-namespaces -o yaml`` command information. Parameters
"--all-namespaces" means collecting information from all projects and "-o yaml"
means the output is in YAML format.

Parsers included in this module are:

OcGetBc - command ``oc get bc -o yaml --all-namespaces``
--------------------------------------------------------

OcGetBuild - command ``oc get build -o yaml --all-namespaces``
--------------------------------------------------------------

OcGetDc - command ``oc get dc -o yaml --all-namespaces``
--------------------------------------------------------

OcGetEgressNetworkPolicy - command ``oc get egressnetworkpolicy -o yaml --all-namespaces``
------------------------------------------------------------------------------------------

OcGetEndPoints - command ``oc get endpoints -o yaml --all-namespaces``
----------------------------------------------------------------------

OcGetEvent - command ``oc get event -o yaml --all-namespaces``
--------------------------------------------------------------

OcGetNode - command ``oc get nodes -o yaml``
--------------------------------------------

OcGetPod - command ``oc get pod -o yaml --all-namespaces``
----------------------------------------------------------

OcGetProject - command ``oc get project -o yaml --all-namespaces``
------------------------------------------------------------------

OcGetPv - command ``oc get pv -o yaml --all-namespaces``
--------------------------------------------------------

OcGetPvc - command ``oc get pvc -o yaml --all-namespaces``
----------------------------------------------------------

OcGetRc - command ``oc get rc -o yaml --all-namespaces``
--------------------------------------------------------

OcGetRole - command ``oc get role -o yaml --all-namespaces``
------------------------------------------------------------

OcGetRolebinding - command ``oc get rolebinding -o yaml --all-namespaces``
--------------------------------------------------------------------------

OcGetRoute - command ``oc get route -o yaml --all-namespaces``
--------------------------------------------------------------

OcGetService - command ``oc get service -o yaml --all-namespaces``
------------------------------------------------------------------

OcGetConfigmap - command ``oc get configmap -o yaml --all-namespaces``
----------------------------------------------------------------------

Examples:
    >>> type(setting_dic)
    <class 'insights.parsers.openshift_get.OcGetService'>
    >>> setting_dic.data['items'][0]['kind']
    'Service'
    >>> setting_dic.data['items'][0]['spec']['clusterIP']
    '172.30.0.1'
    >>> setting_dic.data['items'][0]['metadata']['name']
    'kubernetes'
    >>> setting_dic.data['items'][1]['metadata']['name']
    'router-1'
    >>> "zjj" in setting_dic.data['items'][1]['metadata']['namespace']
    True
"""

from .. import YAMLParser, parser, CommandParser
from insights.specs import Specs


def metadata_name_items(data):
    return dict((item['metadata']['name'], item) for item in data['items'])


@parser(Specs.oc_get_bc)
class OcGetBc(CommandParser, YAMLParser):
    """Class to parse ``oc get bc -o yaml --all-namespaces``"""

    @property
    def build_configs(self):
        """ dict: Returns a dictionary of openshift build configs information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_build)
class OcGetBuild(YAMLParser):
    """Class to parse ``oc get build -o yaml --all-namespaces``"""

    @property
    def started_builds(self):
        """ dict: Returns a dictionary of openshift started build information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_dc)
class OcGetDc(CommandParser, YAMLParser):
    """Class to parse ``oc get dc -o yaml --all-namespaces``"""

    @property
    def deployment_configs(self):
        """ dict: Returns a dictionary of openshift deploymentconfigs information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_egressnetworkpolicy)
class OcGetEgressNetworkPolicy(CommandParser, YAMLParser):
    """Class to parse ``oc get egressnetworkpolicy -o yaml --all-namespaces``"""

    @property
    def egress_network_policies(self):
        """ dict: Returns a dictionary of openshift egress network policy information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_endpoints)
class OcGetEndPoints(CommandParser, YAMLParser):
    """Class to parse ``oc get endpoints -o yaml --all-namespaces``"""

    @property
    def endpoints(self):
        """ dict: Returns a dictionary of openshift endpoints information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_event)
class OcGetEvent(CommandParser, YAMLParser):
    """Class to parse ``oc get event -o yaml --all-namespaces``"""

    @property
    def events(self):
        """ dict: Returns a dictionary of openshift events information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_node)
class OcGetNode(CommandParser, YAMLParser):
    """Class to parse ``oc get nodes -o yaml``"""

    @property
    def nodes(self):
        """ dict: Returns a dictionary of openshift nodes information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_pod)
class OcGetPod(CommandParser, YAMLParser):
    """Class to parse ``oc get pod -o yaml --all-namespaces``"""

    @property
    def pods(self):
        """ dict: Returns a dictionary of openshift pods information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_project)
class OcGetProject(CommandParser, YAMLParser):
    """Class to parse ``oc get project -o yaml --all-namespaces``"""

    @property
    def projects(self):
        """ dict: Returns a dictionary of openshift project information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_pv)
class OcGetPv(CommandParser, YAMLParser):
    """Class to parse ``oc get pv -o yaml --all-namespaces``"""

    @property
    def persistent_volumes(self):
        """ dict: Returns a dictionary of openshift persistent volume information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_pvc)
class OcGetPvc(CommandParser, YAMLParser):
    """Class to parse ``oc get pvc -o yaml --all-namespaces``"""

    @property
    def persistent_volume_claims(self):
        """ dict: Returns a dictionary of openshift persistent volume claim information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_rc)
class OcGetRc(CommandParser, YAMLParser):
    """Class to parse ``oc get rc -o yaml --all-namespaces``"""

    @property
    def replication_controllers(self):
        """ dict: Returns a dictionary of openshift replication controllers information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_role)
class OcGetRole(CommandParser, YAMLParser):
    """Class to parse ``oc get role -o yaml --all-namespaces``"""

    @property
    def roles(self):
        """ dict: Returns a dictionary of openshift role information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_rolebinding)
class OcGetRolebinding(CommandParser, YAMLParser):
    """Class to parse ``oc get rolebinding -o yaml --all-namespaces``"""

    @property
    def rolebindings(self):
        """ dict: Returns a dictionary of openshift rolebind information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_route)
class OcGetRoute(CommandParser, YAMLParser):
    """Class to parse ``oc get route -o yaml --all-namespaces``"""

    @property
    def routes(self):
        """ dict: Returns a dictionary of openshift route information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_service)
class OcGetService(CommandParser, YAMLParser):
    """Class to parse ``oc get service -o yaml --all-namespaces``"""

    @property
    def services(self):
        """ dict: Returns a dictionary of openshift services information."""
        return metadata_name_items(self.data)


@parser(Specs.oc_get_configmap)
class OcGetConfigmap(CommandParser, YAMLParser):
    """Class to parse ``oc get configmap -o yaml --all-namespaces``"""

    @property
    def configmaps(self):
        """ dict: Returns a dictionary of openshift configmaps information."""
        return metadata_name_items(self.data)
