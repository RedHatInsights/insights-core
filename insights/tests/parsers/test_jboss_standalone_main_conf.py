from insights.parsers.jboss_standalone_main_conf import JbossStandaloneConf
from insights.tests import context_wrap
from insights.parsers import jboss_standalone_main_conf
import doctest

JBOSS_STANDALONE_CONFIG = """
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
        <audit-log>
            <formatters>
                <json-formatter name="json-formatter"/>
            </formatters>
            <handlers>
                <file-handler name="file" formatter="json-formatter" path="audit-log.log" relative-to="jboss.server.data.dir"/>
            </handlers>
            <logger log-boot="true" log-read-only="false" enabled="false">
                <handlers>
                    <handler name="file"/>
                </handlers>
            </logger>
        </audit-log>
        <management-interfaces>
            <native-interface security-realm="ManagementRealm">
                <socket-binding native="management-native"/>
            </native-interface>
            <http-interface security-realm="ManagementRealm">
                <socket-binding http="management-http"/>
            </http-interface>
        </management-interfaces>
        <access-control provider="simple">
            <role-mapping>
                <role name="SuperUser">
                    <include>
                        <user name="$local"/>
                    </include>
                </role>
            </role-mapping>
        </access-control>
    </management>
</server>
"""


def test_jboss_standalone_conf():
    jboss_standalone_conf = JbossStandaloneConf(
        context_wrap(JBOSS_STANDALONE_CONFIG, path="/root/jboss/jboss-eap-6.4/standalone/configuration/standalone.xml"))
    assert jboss_standalone_conf is not None
    assert jboss_standalone_conf.file_path == "/root/jboss/jboss-eap-6.4/standalone/configuration/standalone.xml"
    assert jboss_standalone_conf.get_elements(
        ".//management/security-realms/security-realm/authentication/properties")[0].get(
        "relative-to") == 'jboss.server.config.dir'


def test_jboss_standalone_conf_doc_examples():
    env = {
        'JbossStandaloneConf': JbossStandaloneConf,
        'jboss_main_config': JbossStandaloneConf(context_wrap(JBOSS_STANDALONE_CONFIG,
                                                              path='/root/jboss/jboss-eap-6.4/standalone/configuration/standalone.xml'))
    }
    failed, total = doctest.testmod(jboss_standalone_main_conf, globs=env)
    assert failed == 0
