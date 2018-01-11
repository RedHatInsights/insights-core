from ...parsers.jboss_domain_pid_conf_map import JbossDomainPidConfMap
from ...parsers.jboss_domain_conf import JbossDomainConf
from ..jboss_domain_conf import AllJbossDomainConf
from ...combiners import jboss_domain_conf
from ...tests import context_wrap
import doctest

PID_CONF_MAP_1 = '2043|/home/jboss/jboss/machine1/domain/host-master.xml|/home/jboss/jboss/machine1/domain/domain.xml'

PID_CONF_MAP_2 = '2069|/home/jboss/jboss/machine2/domain/host-slave.xml|/home/jboss/jboss/machine2/domain/domain.xml'

HOST_XML_SLAVE = """
<?xml version='1.0' encoding='UTF-8'?>

<host xmlns="urn:jboss:domain:1.7">

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

HOST_XML_MASTER = """
<?xml version='1.0' encoding='UTF-8'?>

<host xmlns="urn:jboss:domain:1.7">

    <domain-controller>
       <local/>
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

DOMAIN_XML = """
<?xml version='1.0' encoding='UTF-8'?>

<domain xmlns="urn:jboss:domain:1.7">

    <system-properties>
        <property name="java.net.preferIPv4Stack" value="true"/>
    </system-properties>

    <management>
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


    <interfaces>
        <interface name="management"/>
        <interface name="public"/>
        <interface name="unsecure"/>
    </interfaces>

    <deployments>
        <deployment name="LogTest.war" runtime-name="LogTest.war">
            <content sha1="8f1b16143e210644920f3bfd6e2a844202dfb471"/>
        </deployment>
        <deployment name="example.war" runtime-name="example.war">
            <content sha1="cbe0a3a1e144bf6d37dba6cba8ccbc46000fef39"/>
        </deployment>
    </deployments>

    <server-groups>
        <server-group name="main-server-group" profile="full">
            <jvm name="default">
                <heap size="1000m" max-size="1000m"/>
                <permgen max-size="256m"/>
            </jvm>
            <socket-binding-group ref="full-sockets"/>
        </server-group>
        <server-group name="other-server-group" profile="full-ha">
            <jvm name="default">
                <heap size="1000m" max-size="1000m"/>
                <permgen max-size="256m"/>
            </jvm>
            <socket-binding-group ref="full-ha-sockets"/>
        </server-group>
    </server-groups>

</domain>
""".strip()


def test_combined():
    context = context_wrap(PID_CONF_MAP_1)
    jboss_pid_map_1 = JbossDomainPidConfMap(context)
    context = context_wrap(PID_CONF_MAP_2)
    jboss_pid_map_2 = JbossDomainPidConfMap(context)
    jboss_pid_maps = [jboss_pid_map_1, jboss_pid_map_2]
    context = context_wrap(HOST_XML_MASTER, path="/home/jboss/jboss/machine1/domain/host-master.xml")
    jboss_master_host_conf = JbossDomainConf(context)
    context = context_wrap(DOMAIN_XML, path="/home/jboss/jboss/machine1/domain/domain.xml")
    jboss_master_domain_conf = JbossDomainConf(context)
    context = context_wrap(HOST_XML_SLAVE, path="/home/jboss/jboss/machine2/domain/host-slave.xml")
    jboss_slave_host_conf = JbossDomainConf(context)
    context = context_wrap(DOMAIN_XML, path="/home/jboss/jboss/machine2/domain/domain.xml")
    jboss_slave_domain_conf = JbossDomainConf(context)
    jboss_domain_confs = [jboss_master_host_conf, jboss_master_domain_conf, jboss_slave_host_conf,
                          jboss_slave_domain_conf]
    all_jboss_domain_conf = AllJbossDomainConf(jboss_pid_maps, jboss_domain_confs)
    assert all_jboss_domain_conf.get_role(2043) == "domain-controller"
    assert len(all_jboss_domain_conf.get_properties(2043, ".//interface")) == 3
    assert all_jboss_domain_conf.get_role(2069) == "host-controller"
    assert all_jboss_domain_conf.get_properties(2069, ".//server-group") == []


def test_combined_doc_examples():
    context = context_wrap(PID_CONF_MAP_1)
    jboss_pid_map_1 = JbossDomainPidConfMap(context)
    context = context_wrap(PID_CONF_MAP_2)
    jboss_pid_map_2 = JbossDomainPidConfMap(context)
    jboss_pid_maps = [jboss_pid_map_1, jboss_pid_map_2]
    context = context_wrap(HOST_XML_MASTER, path="/home/jboss/jboss/machine1/domain/host-master.xml")
    jboss_master_host_conf = JbossDomainConf(context)
    context = context_wrap(DOMAIN_XML, path="/home/jboss/jboss/machine1/domain/domain.xml")
    jboss_master_domain_conf = JbossDomainConf(context)
    context = context_wrap(HOST_XML_SLAVE, path="/home/jboss/jboss/machine2/domain/host-slave.xml")
    jboss_slave_host_conf = JbossDomainConf(context)
    context = context_wrap(DOMAIN_XML, path="/home/jboss/jboss/machine2/domain/domain.xml")
    jboss_slave_domain_conf = JbossDomainConf(context)
    jboss_domain_confs = [jboss_master_host_conf, jboss_master_domain_conf, jboss_slave_host_conf,
                          jboss_slave_domain_conf]
    env = {
        'all_jboss_domain_conf': AllJbossDomainConf(jboss_pid_maps, jboss_domain_confs)
    }
    failed, total = doctest.testmod(jboss_domain_conf, globs=env)
    assert failed == 0
