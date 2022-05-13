from insights.parsers import candlepin_broker
from insights.parsers.candlepin_broker import CandlepinBrokerXML
from insights.tests import context_wrap
import doctest


CANDLEPIN_BROKER_1 = """
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
        <persistence-enabled>true</persistence-enabled>
        <journal-type>NIO</journal-type>
        <journal-pool-files>1</journal-pool-files>
        <create-bindings-dir>true</create-bindings-dir>
        <create-journal-dir>true</create-journal-dir>
        <bindings-directory>/var/lib/candlepin/activemq-artemis/bindings</bindings-directory>
        <journal-directory>/var/lib/candlepin/activemq-artemis/journal</journal-directory>
        <large-messages-directory>/var/lib/candlepin/activemq-artemis/largemsgs</large-messages-directory>
        <paging-directory>/var/lib/candlepin/activemq-artemis/paging</paging-directory>
        <max-disk-usage>99</max-disk-usage>
    <addresses>
            <address name="event.default">
                <multicast>
                    <queue name="event.org.candlepin.audit.LoggingListener" />
                    <queue name="event.org.candlepin.audit.ActivationListener" />
                </multicast>
            </address>

            <address name="katello.candlepin">
                <multicast>
                  <queue max-consumers="1" name="katello_candlepin_event_monitor.candlepin_events" />
                </multicast>
            </address>

            <address name="job">
                <multicast>
                    <queue name="jobs" />
                </multicast>
            </address>
        </addresses>

        <address-settings>
            <address-setting match="event.default">
                <config-delete-queues>FORCE</config-delete-queues>
                <auto-create-queues>true</auto-create-queues>
                <max-size-bytes>10485760</max-size-bytes>


                <page-size-bytes>1048576</page-size-bytes>


                <redelivery-delay>30000</redelivery-delay>
                <max-redelivery-delay>3600000</max-redelivery-delay>
                <redelivery-delay-multiplier>2</redelivery-delay-multiplier>
                <max-delivery-attempts>0</max-delivery-attempts>
            </address-setting>

            <address-setting match="katello.candlepin">
                <auto-create-queues>false</auto-create-queues>
                <max-size-bytes>10485760</max-size-bytes>


                <page-size-bytes>1048576</page-size-bytes>

                <redelivery-delay>0</redelivery-delay>
                <max-delivery-attempts>1</max-delivery-attempts>
            </address-setting>
            <address-setting match="job">
                <auto-create-queues>true</auto-create-queues>
                <max-size-bytes>10485760</max-size-bytes>


                <page-size-bytes>1048576</page-size-bytes>


                <redelivery-delay>30000</redelivery-delay>
                <max-redelivery-delay>3600000</max-redelivery-delay>
                <redelivery-delay-multiplier>2</redelivery-delay-multiplier>
                <max-delivery-attempts>0</max-delivery-attempts>
            </address-setting>
        </address-settings>

        <diverts>
            <divert name="katello_divert">
                <exclusive>false</exclusive>
                <address>event.default</address>
                <filter string="                     (EVENT_TARGET='COMPLIANCE' and EVENT_TYPE='CREATED') OR                     (EVENT_TARGET='SYSTEM_PURPOSE_COMPLIANCE' and EVENT_TYPE='CREATED') OR                     (EVENT_TARGET='POOL' and EVENT_TYPE='CREATED') OR                     (EVENT_TARGET='POOL' and EVENT_TYPE='DELETED') OR                     (EVENT_TARGET='ENTITLEMENT' and EVENT_TYPE='CREATED') OR                     (EVENT_TARGET='ENTITLEMENT' and EVENT_TYPE='DELETED') OR                     (EVENT_TARGET='OWNER_CONTENT_ACCESS_MODE' and EVENT_TYPE='MODIFIED')                 " />
                <forwarding-address>katello.candlepin</forwarding-address>
            </divert>
        </diverts>
    </core>
</configuration>
""".strip()


def test_candlepin_broker():
    broker = CandlepinBrokerXML(context_wrap(CANDLEPIN_BROKER_1))
    page_dirs = broker.get_elements('.//paging-directory')
    assert len(page_dirs) == 1
    assert page_dirs[0].text == '/var/lib/candlepin/activemq-artemis/paging'
    usage_eles = broker.get_elements('.//max-disk-usage')
    assert len(usage_eles) == 1
    assert usage_eles[0].text == '99'


def test_catalina_log_doc_examples():
    env = {
            'broker': CandlepinBrokerXML(context_wrap(CANDLEPIN_BROKER_1)),
          }
    failed, total = doctest.testmod(candlepin_broker, globs=env)
    assert failed == 0
