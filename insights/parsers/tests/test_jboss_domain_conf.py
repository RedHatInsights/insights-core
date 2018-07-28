from ...parsers import jboss_domain_conf
from ...parsers.jboss_domain_conf import JbossDomainConf
from ...tests import context_wrap
import doctest

XML = """
<?xml version='1.0' encoding='UTF-8'?>

<host xmlns="urn:jboss:domain:1.7">

    <management>
        <management-interfaces>
            <native-interface security-realm="ManagementRealm">
                <socket interface="management" port="${jboss.management.native.port:9999}"/>
            </native-interface>
        </management-interfaces>
    </management>

    <domain-controller>
       <remote host="${jboss.domain.master.address}" port="${jboss.domain.master.port:9999}" security-realm="ManagementRealm"/>
    </domain-controller>

    <interfaces>
        <interface name="management">
            <inet-address value="${jboss.bind.address.management:127.0.0.1}"/>
        </interface>
        <interface name="public">
           <inet-address value="${jboss.bind.address:127.0.0.1}"/>
        </interface>
        <interface name="unsecure">
            <!-- Used for IIOP sockets in the standard configuration.
                 To secure JacORB you need to setup SSL -->
            <inet-address value="${jboss.bind.address.unsecure:127.0.0.1}"/>
        </interface>
    </interfaces>

    <servers>
        <server name="server-one" group="main-server-group"/>
        <server name="server-two" group="other-server-group">
            <!-- server-two avoids port conflicts by incrementing the ports in
                 the default socket-group declared in the server-group -->
            <socket-bindings port-offset="150"/>
        </server>
    </servers>
</host>
""".strip()


def test_jboss_domain_conf():
    conf = jboss_domain_conf.JbossDomainConf(context_wrap(XML, path="/home/jboss/jboss/machine1/domain/domain.xml"))
    assert conf.get("/home/jboss/jboss/machine1/domain/domain.xml").get_elements(
        ".//domain-controller")[0].tag == '{urn:jboss:domain:1.7}domain-controller'


def test_jboss_domain_conf_doc_examples():
    env = {
        'JbossDomainConf': JbossDomainConf,
        'jboss_domain_conf': JbossDomainConf(context_wrap(XML, path="/home/jboss/jboss/machine1/domain/domain.xml"))
    }
    failed, total = doctest.testmod(jboss_domain_conf, globs=env)
    assert failed == 0
