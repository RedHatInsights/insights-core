import pytest
from mock.mock import Mock

from insights.core.spec_factory import DatasourceProvider
from insights.core.dr import SkipComponent
from insights.specs.datasources.candlepin_broker import candlepin_broker, LocalSpecs


CANDLEPIN_BROKER = """
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

        <security-settings>
            <security-setting match="katello.candlepin.#">
                <permission type="consume" roles="candlepinEventsConsumer"/>
            </security-setting>
            <security-setting match="#">
                <permission type="createAddress" roles="invm-role"/>
                <permission type="deleteAddress" roles="invm-role"/>
                <permission type="createDurableQueue" roles="invm-role"/>
                <permission type="deleteDurableQueue" roles="invm-role"/>
                <permission type="createNonDurableQueue" roles="invm-role"/>
                <permission type="deleteNonDurableQueue" roles="invm-role"/>
                <permission type="send" roles="invm-role"/>
                <permission type="consume" roles="invm-role"/>
                <permission type="browse" roles="invm-role"/>
                <permission type="manage" roles="invm-role"/>
            </security-setting>
        </security-settings>

        <!-- Silence warnings on server startup -->
        <cluster-user></cluster-user>
        <cluster-password></cluster-password>
    </core>
</configuration>
""".strip()

CANDLEPIN_BROKER_NO_SENSITIVE_INFO = """
<configuration xmlns="urn:activemq"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:schemaLocation="urn:activemq /schema/artemis-configuration.xsd">
    <core xmlns="urn:activemq:core" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="urn:activemq:core ">

        <security-enabled>true</security-enabled>

        <security-settings>
            <security-setting match="katello.candlepin.#">
                <permission type="consume" roles="candlepinEventsConsumer"/>
            </security-setting>
            <security-setting match="#">
                <permission type="createAddress" roles="invm-role"/>
                <permission type="deleteAddress" roles="invm-role"/>
                <permission type="createDurableQueue" roles="invm-role"/>
                <permission type="deleteDurableQueue" roles="invm-role"/>
                <permission type="createNonDurableQueue" roles="invm-role"/>
                <permission type="deleteNonDurableQueue" roles="invm-role"/>
                <permission type="send" roles="invm-role"/>
                <permission type="consume" roles="invm-role"/>
                <permission type="browse" roles="invm-role"/>
                <permission type="manage" roles="invm-role"/>
            </security-setting>
        </security-settings>

        <!-- Silence warnings on server startup -->
        <cluster-user></cluster-user>
    </core>
</configuration>
""".strip()

CANDLEPIN_BROKER_BAD = """
<config>
    <core/>
</configuration>
""".strip()


CANDLEPIN_BROKER_XML = """
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:activemq /schema/artemis-configuration.xsd">
    <core xsi:schemaLocation="urn:activemq:core ">
        <security-enabled>true</security-enabled>
        <security-settings>
            <security-setting match="katello.candlepin.#">
                <permission roles="candlepinEventsConsumer" type="consume" />
            </security-setting>
            <security-setting match="#">
                <permission roles="invm-role" type="createAddress" />
                <permission roles="invm-role" type="deleteAddress" />
                <permission roles="invm-role" type="createDurableQueue" />
                <permission roles="invm-role" type="deleteDurableQueue" />
                <permission roles="invm-role" type="createNonDurableQueue" />
                <permission roles="invm-role" type="deleteNonDurableQueue" />
                <permission roles="invm-role" type="send" />
                <permission roles="invm-role" type="consume" />
                <permission roles="invm-role" type="browse" />
                <permission roles="invm-role" type="manage" />
            </security-setting>
        </security-settings>
        <cluster-user />
        </core>
</configuration>
""".strip()


CANDLE_BROKER_NO_SENTISVE_INFO = """
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:activemq /schema/artemis-configuration.xsd">
    <core xsi:schemaLocation="urn:activemq:core ">
        <security-enabled>true</security-enabled>
        <security-settings>
            <security-setting match="katello.candlepin.#">
                <permission roles="candlepinEventsConsumer" type="consume" />
            </security-setting>
            <security-setting match="#">
                <permission roles="invm-role" type="createAddress" />
                <permission roles="invm-role" type="deleteAddress" />
                <permission roles="invm-role" type="createDurableQueue" />
                <permission roles="invm-role" type="deleteDurableQueue" />
                <permission roles="invm-role" type="createNonDurableQueue" />
                <permission roles="invm-role" type="deleteNonDurableQueue" />
                <permission roles="invm-role" type="send" />
                <permission roles="invm-role" type="consume" />
                <permission roles="invm-role" type="browse" />
                <permission roles="invm-role" type="manage" />
            </security-setting>
        </security-settings>
        <cluster-user />
    </core>
</configuration>
""".strip()

RELATIVE_PATH = '/etc/candlepin/broker.xml'


def test_candlepin_broker():
    candlepin_broker_file = Mock()
    candlepin_broker_file.content = CANDLEPIN_BROKER.splitlines()
    broker = {LocalSpecs.candlepin_broker_input: candlepin_broker_file}
    result = candlepin_broker(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=CANDLEPIN_BROKER_XML.splitlines(), relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path


def test_candlepin_broker_bad():
    candlepin_broker_file = Mock()
    candlepin_broker_file.content = CANDLEPIN_BROKER_BAD.splitlines()
    broker = {LocalSpecs.candlepin_broker_input: candlepin_broker_file}
    with pytest.raises(SkipComponent) as e:
        candlepin_broker(broker)
    assert 'Unexpected exception' in str(e)


def test_candlpin_broker_no_sensitive_info():
    candlepin_broker_file = Mock()
    candlepin_broker_file.content = CANDLEPIN_BROKER_NO_SENSITIVE_INFO.splitlines()
    broker = {LocalSpecs.candlepin_broker_input: candlepin_broker_file}
    result = candlepin_broker(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=CANDLE_BROKER_NO_SENTISVE_INFO.splitlines(), relative_path=RELATIVE_PATH)
    assert result.content == expected.content
    assert result.relative_path == expected.relative_path
