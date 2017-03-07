"""
oc get XX --all-namespaces -o yaml - Command
============================================

``oc get`` command is from openshift, and used to list the usage info that is
pods info, dc info, services info, e.g.  This shared mapper is used to parse
``oc get XX --all-namespaces -o yaml`` command information. Parameters
"--all-namespaces" means collecting information from all projects and "-o yaml"
eans the output format is yaml.

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

import yaml
from .. import Mapper, mapper


@mapper('oc_get_pod')
class OcGetPod(Mapper):
    """Class to parse ``oc get pod -o yaml --all-namespaces``"""

    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))

    def get_pod(self):
        """ dict: Returns a dictionary of openshift pods information."""
        pod_items = {}
        for pod in self.data["items"]:
            pod_items[pod["metadata"]["name"]] = pod
        return pod_items


@mapper('oc_get_dc')
class OcGetDc(Mapper):
    """Class to parse ``oc get dc -o yaml --all-namespaces``"""

    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))

    def get_dc(self):
        """ dict: Returns a dictionary of openshift deploymentconfigs information."""
        dc_items = {}
        for dc in self.data["items"]:
            dc_items[dc["metadata"]["name"]] = dc
        return dc_items


@mapper('oc_get_service')
class OcGetService(Mapper):
    """Class to parse ``oc get service -o yaml --all-namespaces``"""

    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))

    def get_service(self):
        """ dict: Returns a dictionary of openshift services information."""
        service_items = {}
        for service in self.data["items"]:
            service_items[service["metadata"]["name"]] = service
        return service_items


@mapper('oc_get_rolebinding')
class OcGetRolebinding(Mapper):
    """Class to parse ``oc get rolebinding -o yaml --all-namespaces``"""

    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))

    def get_rolebind(self):
        """ dict: Returns a dictionary of openshift rolebind information."""
        rolebind_items = {}
        for rolebind in self.data["items"]:
            rolebind_items[rolebind["metadata"]["name"]] = rolebind
        return rolebind_items


@mapper('oc_get_project')
class OcGetProject(Mapper):
    """Class to parse ``oc get project -o yaml --all-namespaces``"""

    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))

    def get_project(self):
        """ dict: Returns a dictionary of openshift project information."""
        project_items = {}
        for project in self.data["items"]:
            project_items[project["metadata"]["name"]] = project
        return project_items


@mapper('oc_get_role')
class OcGetRole(Mapper):
    """Class to parse ``oc get role -o yaml --all-namespaces``"""

    def parse_content(self, content):
        self.data = yaml.load('\n'.join(content))

    def get_role(self):
        """ dict: Returns a dictionary of openshift role information."""
        role_items = {}
        for role in self.data["items"]:
            role_items[role["metadata"]["name"]] = role
        return role_items
