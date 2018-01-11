"""
JBoss domain mode main configuration - file ``$JBOSS_BASE_DIR/host.xml`` or ``$JBOSS_BASE_DIR/domain.xml``
==========================================================================================================

There are two main configuration files host.xml and domain.xml to configure a host-controller and domain-controller
in JBoss domain mode. These two files have similar format.
This parser does not really parse all the content. Instead, it only keep the link between
file path and ``JbossDomainConf``. Combiner combiners.jboss_domain_conf will base on this parser to do real parsing.

Sample input::

    <?xml version='1.0' encoding='UTF-8'?>
    <server xmlns="urn:jboss:domain:1.7">
        <management>
            <security-realms>
                <security-realm name="ManagementRealm">
                    <authentication>
                        <local default-user="$local" skip-group-loading="true"/>
                        <properties path="mgmt-users.properties" relative-to="jboss.server.config.dir"/>
                    </authentication>
                    <authorization map-groups-to-roles="false">
                        <properties path="mgmt-groups.properties" relative-to="jboss.server.config.dir"/>
                    </authorization>
                </security-realm>
                <security-realm name="ApplicationRealm">
                    <authentication>
                        <local default-user="$local" allowed-users="*" skip-group-loading="true"/>
                        <properties path="application-users.properties" relative-to="jboss.server.config.dir"/>
                    </authentication>
                    <authorization>
                        <properties path="application-roles.properties" relative-to="jboss.server.config.dir"/>
                    </authorization>
                </security-realm>
            </security-realms>
        </management>
    </server>

Examples:

    >>> jboss_domain_conf.get("/home/jboss/jboss/machine1/domain/domain.xml").get_elements(".//domain-controller")[0].tag
    '{urn:jboss:domain:1.7}domain-controller'

"""

from .. import parser, XMLParser

from insights.specs import jboss_domain_config


@parser(jboss_domain_config)
class JbossDomainConf(XMLParser):
    """
    Overwrite :func:`parse_dom`. ``self.data`` keeps parsed dict.
    The key of the dict is configuration file path and value is ``JbossDomainConf`` object itself.
    """

    def parse_dom(self):
        return {self.file_path: self}
