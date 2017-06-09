"""
oc get XX --all-namespaces -o yaml - Command
============================================

``oc get`` command is from openshift, and used to list the usage info that is
pods info, dc info, services info, e.g.  This shared parser is used to parse
``oc get XX --all-namespaces -o yaml`` command information. Parameters
"--all-namespaces" means collecting information from all projects and "-o yaml"
means the output is in YAML format.

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


def metadata_name_items(data):
    return {item['metadata']['name']: item for item in data['items']}


@parser('oc_get_pod')
class OcGetPod(YAMLParser):
    """Class to parse ``oc get pod -o yaml --all-namespaces``"""

    def get_pod(self):
        """ dict: Returns a dictionary of openshift pods information."""
        return metadata_name_items(self.data)


@parser('oc_get_dc')
class OcGetDc(YAMLParser):
    """Class to parse ``oc get dc -o yaml --all-namespaces``"""

    def get_dc(self):
        """ dict: Returns a dictionary of openshift deploymentconfigs information."""
        return metadata_name_items(self.data)


@parser('oc_get_service')
class OcGetService(YAMLParser):
    """Class to parse ``oc get service -o yaml --all-namespaces``"""

    def get_service(self):
        """ dict: Returns a dictionary of openshift services information."""
        return metadata_name_items(self.data)


@parser('oc_get_rolebinding')
class OcGetRolebinding(YAMLParser):
    """Class to parse ``oc get rolebinding -o yaml --all-namespaces``"""

    def get_rolebind(self):
        """ dict: Returns a dictionary of openshift rolebind information."""
        return metadata_name_items(self.data)


@parser('oc_get_project')
class OcGetProject(YAMLParser):
    """Class to parse ``oc get project -o yaml --all-namespaces``"""

    def get_project(self):
        """ dict: Returns a dictionary of openshift project information."""
        return metadata_name_items(self.data)


@parser('oc_get_role')
class OcGetRole(YAMLParser):
    """Class to parse ``oc get role -o yaml --all-namespaces``"""

    def get_role(self):
        """ dict: Returns a dictionary of openshift role information."""
        return metadata_name_items(self.data)


@parser('oc_get_pv')
class OcGetPv(YAMLParser):
    """Class to parse ``oc get pv -o yaml --all-namespaces``"""

    def get_pv(self):
        """ dict: Returns a dictionary of openshift pv information."""
        return metadata_name_items(self.data)


@parser('oc_get_pvc')
class OcGetPvc(YAMLParser):
    """Class to parse ``oc get pvc -o yaml --all-namespaces``"""

    def get_pvc(self):
        """ dict: Returns a dictionary of openshift pvc information."""
        return metadata_name_items(self.data)
