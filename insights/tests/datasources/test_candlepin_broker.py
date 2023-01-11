import pytest

from mock.mock import Mock

from insights.core import ET
from insights.core.exceptions import SkipComponent
from insights.core.spec_factory import DatasourceProvider
from insights.specs.default import candlepin_broker


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


def xml_check_removed(result):
    root = ET.fromstring('\n'.join(result))
    assert root is not None
    core_ele = root.find('core')
    assert core_ele is not None

    search_tags = ['cluster-password', 'acceptors']
    for tag in search_tags:
        found = core_ele.find(tag)
        assert found is None, 'Tag {} should not be in result'.format(tag)


def xml_compare(result, expected):
    root_result = ET.fromstring('\n'.join(result))
    root_expected = ET.fromstring('\n'.join(expected))

    re_core_ele = root_result.find('core')
    assert re_core_ele is not None
    ex_core_ele = root_expected.find('core')
    assert ex_core_ele is not None

    search_tags = ['cluster-user', 'security-enabled']
    for tag in search_tags:
        ex_found = ex_core_ele.find(tag)
        if ex_found is not None:
            re_found = re_core_ele.find(tag)
            assert re_found is not None, 'Tag {} is in expected but not in result'.format(tag)
            assert re_found.text == ex_found.text, 'Tag {} text is different in expected and result'.format(tag)

    ex_settings = ex_core_ele.find('security-settings')
    if ex_settings is not None:
        re_settings = re_core_ele.find('security-settings')
        assert re_found is not None, 'Tag security-settings is in expected but not in result'
        assert re_found.text == ex_found.text, 'Tag {} text is different in expected and result'.format(tag)
        ex_settings_dict = {}
        re_settings_dict = {}
        for setting in ex_settings.findall('security-setting'):
            ex_settings_dict[setting.get('match')] = []
            for perm in setting.findall('permission'):
                ex_settings_dict[setting.get('match')].append((perm.get('roles'), perm.get('type')))
        for setting in re_settings.findall('security-setting'):
            re_settings_dict[setting.get('match')] = []
            for perm in setting.findall('permission'):
                re_settings_dict[setting.get('match')].append((perm.get('roles'), perm.get('type')))
        assert ex_settings_dict == re_settings_dict


def test_candlepin_broker():
    candlepin_broker_file = Mock()
    candlepin_broker_file.content = CANDLEPIN_BROKER.splitlines()
    broker = {candlepin_broker.LocalSpecs.candlepin_broker_input: candlepin_broker_file}
    result = candlepin_broker.candlepin_broker(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=CANDLEPIN_BROKER_XML.splitlines(), relative_path=RELATIVE_PATH)
    xml_check_removed(result.content)
    xml_compare(result.content, expected.content)
    assert result.relative_path == expected.relative_path


def test_candlepin_broker_bad():
    candlepin_broker_file = Mock()
    candlepin_broker_file.content = CANDLEPIN_BROKER_BAD.splitlines()
    broker = {candlepin_broker.LocalSpecs.candlepin_broker_input: candlepin_broker_file}
    with pytest.raises(SkipComponent) as e:
        candlepin_broker.candlepin_broker(broker)
    assert 'Unexpected exception' in str(e)


def test_candlpin_broker_no_sensitive_info():
    candlepin_broker_file = Mock()
    candlepin_broker_file.content = CANDLEPIN_BROKER_NO_SENSITIVE_INFO.splitlines()
    broker = {candlepin_broker.LocalSpecs.candlepin_broker_input: candlepin_broker_file}
    result = candlepin_broker.candlepin_broker(broker)
    assert result is not None
    assert isinstance(result, DatasourceProvider)
    expected = DatasourceProvider(content=CANDLE_BROKER_NO_SENTISVE_INFO.splitlines(), relative_path=RELATIVE_PATH)
    xml_check_removed(result.content)
    xml_compare(result.content, expected.content)
    assert result.relative_path == expected.relative_path
