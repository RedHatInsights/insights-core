"""
Custom datasources for candlepin broker.xml
"""
from insights.core.context import HostContext
from insights.core.dr import SkipComponent
from insights.core.plugins import datasource
from insights.core.spec_factory import DatasourceProvider, simple_file
from insights.specs import Specs
from insights.specs.default import SatelliteVersion
from insights.core import ET


class LocalSpecs(Specs):
    """ Local specs used only by candlepin_broker datasources """

    candlepin_broker_input = simple_file("/etc/candlepin/broker.xml")
    """ Returns the contents of the file ``/etc/candlepin/broker.xml`` """


@datasource(LocalSpecs.candlepin_broker_input, HostContext, SatelliteVersion)
def candlepin_broker(broker):
    """
    This datasource provides the candlepn broker configuration information
    collected from ``/etc/candlepin/broker.xml``.

    Typical content of ``/etc/candlepin/broker.xml`` file is::

        <configuration xmlns="urn:activemq"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="urn:activemq /schema/artemis-configuration.xsd">
            <core xmlns="urn:activemq:core" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="urn:activemq:core ">
                <acceptors>
                    <acceptor name="in-vm">vm://0</acceptor>
                    <acceptor name="stomp">tcp://localhost:61613?protocols=STOMP;useEpoll=false;sslEnabled=true;trustStorePath=/etc/candlepin/certs/truststore;trustStorePassword=CDX9i3K5uPPBzcNtzz5tcycVf5PuXA5w;keyStorePath=/etc/candlepin/certs/keystore;keyStorePassword=4iBpTS45VZjFmVdNzRhRKNXtxbsH5Dij;needClientAuth=true</acceptor>
                </acceptors>
                <security-enabled>true</security-enabled>
            </core>
        </configuration>

    Note:
        This datasource may be executed using the following command:

        ``insights cat --no-header candlepin_broker``

    Returns:
        str: XML string after removeing sensitive information.

    Raises:
        SkipComponent: When the path does not exist or any exception occurs.
    """

    relative_path = '/etc/candlepin/broker.xml'
    try:
        content = broker[LocalSpecs.candlepin_broker_input].content
        if content:
            root = ET.fromstring('\n'.join(content))
            # remove namespace before save to avoid urgly search
            for node in list(root.iter()):
                prefix, has_namespace, postfix = node.tag.rpartition('}')
                if has_namespace:
                    node.tag = postfix
            # remove sensitive data
            core_ele = root.find('core')
            passwd_ele = core_ele.find('cluster-password')
            if passwd_ele is not None:
                core_ele.remove(passwd_ele)
            acc_ele = core_ele.find('acceptors')
            if acc_ele:
                core_ele.remove(acc_ele)
            return DatasourceProvider(
                content=[line for line in ET.tostring(root).decode('utf-8').splitlines() if line.strip()],
                relative_path=relative_path
            )
    except Exception as e:
        raise SkipComponent("Unexpected exception:{e}".format(e=str(e)))
    raise SkipComponent()
