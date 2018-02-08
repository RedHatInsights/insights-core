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

OcGetDc - command ``oc get dc -o yaml --all-namespaces``
--------------------------------------------------------

OcGetEgressNetworkPolicy - command ``oc get egressnetworkpolicy -o yaml --all-namespaces``
------------------------------------------------------------------------------------------

OcGetEndPoints - command ``oc get endpoints -o yaml --all-namespaces``
----------------------------------------------------------------------

OcGetEvent - command ``oc get event -o yaml --all-namespaces``
--------------------------------------------------------------

OcGetNode - command ``oc get node -o yaml``
-------------------------------------------

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

OcGetService - command ``oc get service -o yaml --all-namespaces``
------------------------------------------------------------------

Examples:
    >>> setting_dic = shared[OcGetService]
    >>> setting_dic.data['items'][0]['kind']
    'Service'
    >>> setting_dic.data['items'][0]['spec']['clusterIP']
    '172.30.0.1'
    >>> setting_dic.data['items'][0]['metadata']['name']
    'kubernetes'
    >>> setting_dic.data['items'][1]['metadata']['name']
    'docker-registry'
    >>> "openshift" in setting_dic.data['items'][1]['metadata']['namespace']
    True
"""

from .. import YAMLParser, parser
from insights.util import deprecated


def metadata_name_items(data):
    return {item['metadata']['name']: item for item in data['items']}


@parser('oc_get_bc')
class OcGetBc(YAMLParser):
    """Class to parse ``oc get bc -o yaml --all-namespaces``"""

    @property
    def build_configs(self):
        """ dict: Returns a dictionary of openshift build configs information."""
        return metadata_name_items(self.data)

    def get_bc(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`build_configs` instead.
        """
        deprecated(self.get_bc, "Deprecated method, please use the :meth:`build_configs` instead")
        return metadata_name_items(self.data)


@parser('oc_get_dc')
class OcGetDc(YAMLParser):
    """Class to parse ``oc get dc -o yaml --all-namespaces``"""

    @property
    def deployment_configs(self):
        """ dict: Returns a dictionary of openshift deploymentconfigs information."""
        return metadata_name_items(self.data)

    def get_dc(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`deployment_configs` instead.
        """
        deprecated(self.get_dc, "Deprecated method, please use the :meth:`deployment_configs` instead")
        return metadata_name_items(self.data)


@parser('oc_get_egressnetworkpolicy')
class OcGetEgressNetworkPolicy(YAMLParser):
    """Class to parse ``oc get egressnetworkpolicy -o yaml --all-namespaces``"""

    @property
    def egress_network_policies(self):
        """ dict: Returns a dictionary of openshift egress network policies information."""
        return metadata_name_items(self.data)


@parser('oc_get_endpoints')
class OcGetEndPoints(YAMLParser):
    """Class to parse ``oc get endpoints -o yaml --all-namespaces``"""

    @property
    def endpoints(self):
        """ dict: Returns a dictionary of openshift endpoints information."""
        return metadata_name_items(self.data)

    def get_endpoints(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`endpoints` instead.
        """
        deprecated(self.get_endpoints, "Deprecated method, please use the :meth:`endpoints` instead")
        return metadata_name_items(self.data)


@parser('oc_get_event')
class OcGetEvent(YAMLParser):
    """Class to parse ``oc get event -o yaml --all-namespaces``"""

    @property
    def events(self):
        """ dict: Returns a dictionary of openshift events information."""
        return metadata_name_items(self.data)


@parser('oc_get_node')
class OcGetNode(YAMLParser):
    """Class to parse ``oc get node -o yaml --all-namespaces``"""

    @property
    def nodes(self):
        """ dict: Returns a dictionary of openshift nodes information."""
        return metadata_name_items(self.data)


@parser('oc_get_pod')
class OcGetPod(YAMLParser):
    """Class to parse ``oc get pod -o yaml --all-namespaces``"""

    @property
    def pods(self):
        """ dict: Returns a dictionary of openshift pods information."""
        return metadata_name_items(self.data)

    def get_pod(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`pods` instead.
        """
        deprecated(self.get_pod, "Deprecated method, please use the :meth:`pods` instead")
        return metadata_name_items(self.data)


@parser('oc_get_project')
class OcGetProject(YAMLParser):
    """Class to parse ``oc get project -o yaml --all-namespaces``"""

    @property
    def projects(self):
        """ dict: Returns a dictionary of openshift projects information."""
        return metadata_name_items(self.data)

    def get_project(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`projects` instead.
        """
        deprecated(self.get_project, "Deprecated method, please use the :meth:`projects` instead")
        return metadata_name_items(self.data)


@parser('oc_get_pv')
class OcGetPv(YAMLParser):
    """Class to parse ``oc get pv -o yaml --all-namespaces``"""

    @property
    def persistent_volumes(self):
        """ dict: Returns a dictionary of openshift persistent volumes information."""
        return metadata_name_items(self.data)

    def get_pv(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`persistent_volumes` instead.
        """
        deprecated(self.get_pv, "Deprecated method, please use the :meth:`persistent_volumes` instead")
        return metadata_name_items(self.data)


@parser('oc_get_pvc')
class OcGetPvc(YAMLParser):
    """Class to parse ``oc get pvc -o yaml --all-namespaces``"""

    @property
    def persistent_volume_claims(self):
        """ dict: Returns a dictionary of openshift persistent volume claims information."""
        return metadata_name_items(self.data)

    def get_pvc(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`persistent_volume_claims` instead.
        """
        deprecated(self.get_pvc, "Deprecated method, please use the :meth:`persistent_volume_claims` instead")
        return metadata_name_items(self.data)


@parser('oc_get_rc')
class OcGetRc(YAMLParser):
    """Class to parse ``oc get rc -o yaml --all-namespaces``"""

    @property
    def replication_controllers(self):
        """ dict: Returns a dictionary of openshift replication controllers information."""
        return metadata_name_items(self.data)


@parser('oc_get_role')
class OcGetRole(YAMLParser):
    """Class to parse ``oc get role -o yaml --all-namespaces``"""

    @property
    def roles(self):
        """ dict: Returns a dictionary of openshift roles information."""
        return metadata_name_items(self.data)

    def get_role(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`roles` instead.
        """
        deprecated(self.get_role, "Deprecated method, please use the :meth:`roles` instead")
        return metadata_name_items(self.data)


@parser('oc_get_rolebinding')
class OcGetRolebinding(YAMLParser):
    """Class to parse ``oc get rolebinding -o yaml --all-namespaces``"""

    @property
    def rolebindings(self):
        """ dict: Returns a dictionary of openshift rolebindings information."""
        return metadata_name_items(self.data)

    def get_rolebind(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`rolebindings` instead.
        """
        deprecated(self.get_rolebind, "Deprecated method, please use the :meth:`rolebindings` instead")
        return metadata_name_items(self.data)


@parser('oc_get_service')
class OcGetService(YAMLParser):
    """Class to parse ``oc get service -o yaml --all-namespaces``"""

    @property
    def services(self):
        """ dict: Returns a dictionary of openshift services information."""
        return metadata_name_items(self.data)

    def get_service(self):
        """
        .. warning::
            Deprecated method, please use the
            :meth:`services` instead.
        """
        deprecated(self.get_service, "Deprecated method, please use the :meth:`services` instead")
        return metadata_name_items(self.data)
