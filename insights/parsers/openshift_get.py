"""
OpenShift Get commands
======================

``oc get`` command is from openshift used to list the usage info - e.g.
pods info, dc info, services info, etc.  This shared parser is used to parse
``oc get XX --all-namespaces -o yaml`` command information. Parameters
"--all-namespaces" means collecting information from all projects and "-o yaml"
means the output is in YAML format.

Parsers included in this module are:

OcGetDc - command ``oc get dc -o yaml --all-namespaces``
--------------------------------------------------------

OcGetEndPoints - command ``oc get endpoints -o yaml --all-namespaces``
----------------------------------------------------------------------

OcGetPod - command ``oc get pod -o yaml --all-namespaces``
----------------------------------------------------------

OcGetProject - command ``oc get project -o yaml --all-namespaces``
------------------------------------------------------------------

OcGetPv - command ``oc get pv -o yaml --all-namespaces``
--------------------------------------------------------

OcGetPvc - command ``oc get pvc -o yaml --all-namespaces``
----------------------------------------------------------

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
from insights.specs import oc_get_dc
from insights.specs import oc_get_endpoints
from insights.specs import oc_get_pod
from insights.specs import oc_get_project
from insights.specs import oc_get_pv
from insights.specs import oc_get_pvc
from insights.specs import oc_get_role
from insights.specs import oc_get_rolebinding
from insights.specs import oc_get_service


def metadata_name_items(data):
    return dict((item['metadata']['name'], item) for item in data['items'])


@parser(oc_get_pod)
class OcGetPod(YAMLParser):
    """Class to parse ``oc get pod -o yaml --all-namespaces``"""

    def get_pod(self):
        """ dict: Returns a dictionary of openshift pods information."""
        return metadata_name_items(self.data)


@parser(oc_get_dc)
class OcGetDc(YAMLParser):
    """Class to parse ``oc get dc -o yaml --all-namespaces``"""

    def get_dc(self):
        """ dict: Returns a dictionary of openshift deploymentconfigs information."""
        return metadata_name_items(self.data)


@parser(oc_get_service)
class OcGetService(YAMLParser):
    """Class to parse ``oc get service -o yaml --all-namespaces``"""

    def get_service(self):
        """ dict: Returns a dictionary of openshift services information."""
        return metadata_name_items(self.data)


@parser(oc_get_rolebinding)
class OcGetRolebinding(YAMLParser):
    """Class to parse ``oc get rolebinding -o yaml --all-namespaces``"""

    def get_rolebind(self):
        """ dict: Returns a dictionary of openshift rolebind information."""
        return metadata_name_items(self.data)


@parser(oc_get_project)
class OcGetProject(YAMLParser):
    """Class to parse ``oc get project -o yaml --all-namespaces``"""

    def get_project(self):
        """ dict: Returns a dictionary of openshift project information."""
        return metadata_name_items(self.data)


@parser(oc_get_role)
class OcGetRole(YAMLParser):
    """Class to parse ``oc get role -o yaml --all-namespaces``"""

    def get_role(self):
        """ dict: Returns a dictionary of openshift role information."""
        return metadata_name_items(self.data)


@parser(oc_get_pv)
class OcGetPv(YAMLParser):
    """Class to parse ``oc get pv -o yaml --all-namespaces``"""

    def get_pv(self):
        """ dict: Returns a dictionary of openshift pv information."""
        return metadata_name_items(self.data)


@parser(oc_get_pvc)
class OcGetPvc(YAMLParser):
    """Class to parse ``oc get pvc -o yaml --all-namespaces``"""

    def get_pvc(self):
        """ dict: Returns a dictionary of openshift pvc information."""
        return metadata_name_items(self.data)


@parser(oc_get_endpoints)
class OcGetEndPoints(YAMLParser):
    """Class to parse ``oc get endpoints -o yaml --all-namespaces``"""

    def get_endpoints(self):
        """ dict: Returns a dictionary of openshift endpoints information."""
        return metadata_name_items(self.data)
