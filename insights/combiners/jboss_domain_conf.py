"""
AllJbossDomainConf - Combiner for parsing JBoss domain configuration files
==========================================================================

Combiner for parsing all the JBoss domain configuration files
"""

from insights.core.plugins import combiner
from insights.parsers.jboss_domain_conf import JbossDomainConf
from insights.parsers.jboss_domain_pid_conf_map import JbossDomainPidConfMap

HOST_CONTROLLER = "host-controller"
DOMAIN_CONTROLLER = "domain-controller"


@combiner(JbossDomainPidConfMap, JbossDomainConf)
class AllJbossDomainConf(object):
    """
    A combiner for parsing all the JBoss domain configuration files.

    Examples:
        >>> all_jboss_domain_conf.get_role(2043)
        'domain-controller'
        >>> len(all_jboss_domain_conf.get_properties(2043, ".//interface"))
        3
        >>> all_jboss_domain_conf.get_role(2069)
        'host-controller'
        >>> all_jboss_domain_conf.get_properties(2069, ".//server-group")
        []

    Attributes:
        results (dict): All the parsed results. The key of the dict is pid and value is a dict.
                        This sub-dict includes keys 'role', 'host_conf' and 'domain_conf'
    """

    def __init__(self, jboss_map_list, jboss_conf_list):
        jboss_map_dict = {}
        for jboss_map in jboss_map_list:
            for pid, host_domain_paths in jboss_map.data.items():
                jboss_map_dict[pid] = host_domain_paths

        jboss_conf_dict = {}
        for jboss_conf in jboss_conf_list:
            for path, conf in jboss_conf.data.items():
                jboss_conf_dict[path] = conf

        results = {}
        for pid, host_domain_paths in jboss_map_dict.items():
            properties = {}
            host_xml_path, domain_xml_path = host_domain_paths
            host_conf = jboss_conf_dict.get(host_xml_path)
            domain_conf = jboss_conf_dict.get(domain_xml_path)
            role = HOST_CONTROLLER
            if len(host_conf.get_elements('.//domain-controller/remote')) == 0:
                role = DOMAIN_CONTROLLER
            properties['role'] = role
            properties['host_conf'] = host_conf
            properties['domain_conf'] = domain_conf
            results[pid] = properties
        self.results = results

    def get_properties(self, pid, element):
        """
        Returns the list of certain properties.

        Parameters:
            pid (int): The process id
            element (str): XPath expression of certain property

        Returns:
            (list): The list of certain property
        """
        conf_file_dict = self.results.get(pid, None)
        properties = []
        if conf_file_dict:
            # host.xml and domain.xml are combined to configure a host-controller or domain-controller.
            # If the same property is defined both in host.xml and domain.xml, value in host.xml will
            # overwrite the value set in domain.xml.
            # domain-controller uses its own domain.xml and host.xml. But host-controller uses domain.xml
            # on domain-controller(not local) and host.xml(local). Since we can not get remote domain.xml,
            # here we can only get properties in host.xml for a host-controller.
            if conf_file_dict['role'] == DOMAIN_CONTROLLER:
                host_conf_prop = conf_file_dict['host_conf'].get_elements(element)
                domain_conf_prop = conf_file_dict['domain_conf'].get_elements(element)
                properties = host_conf_prop if host_conf_prop else domain_conf_prop
            else:
                properties = conf_file_dict['host_conf'].get_elements(element)
        return properties

    def get_role(self, pid):
        """
        Returns the role of controller(host-controller or domain-controller)

        Parameters:
            pid (int): The process id

        Returns:
            (str): The role of controller(host-controller or domain-controller)
        """
        conf_file_dict = self.results.get(pid, None)
        if conf_file_dict:
            return conf_file_dict['role']
        return None
