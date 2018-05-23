"""
JBoss standalone mode main configuration - file ``$JBOSS_BASE_DIR/standalone.xml``
==================================================================================
This parser reads the XML in the JBoss standalone mode main configuration file.

.. note::
        Please refer to its super-class :class:`insights.core.XMLParser` for more details.


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

    >>> jboss_main_config.file_path
    '/root/jboss/jboss-eap-6.4/standalone/configuration/standalone.xml'
    >>> properties = sorted(jboss_main_config.get_elements(".//management/security-realms/security-realm/authentication/properties"), key=lambda e: e.tag)
    >>> properties[0].get("relative-to")
    'jboss.server.config.dir'

"""

from .. import XMLParser, parser

from insights.specs import Specs


@parser(Specs.jboss_standalone_main_config)
class JbossStandaloneConf(XMLParser):
    """
    Read the XML in the JBoss standalone mode main configuration file
    """

    pass
