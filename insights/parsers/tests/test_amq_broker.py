#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest

from insights.parsers.amq_broker import AMQBroker
from insights.tests import context_wrap

BROKER_DOT_XML = """
<?xml version='1.0'?>
<!--
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
-->

<configuration xmlns="urn:activemq"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xi="http://www.w3.org/2001/XInclude"
               xsi:schemaLocation="urn:activemq /schema/artemis-configuration.xsd">

   <core xmlns="urn:activemq:core" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="urn:activemq:core ">

      <name>0.0.0.0</name>


      <persistence-enabled>true</persistence-enabled>

      <!-- this could be ASYNCIO, MAPPED, NIO
           ASYNCIO: Linux Libaio
           MAPPED: mmap files
           NIO: Plain Java Files
       -->
      <journal-type>NIO</journal-type>

      <paging-directory>data/paging</paging-directory>

      <bindings-directory>data/bindings</bindings-directory>

      <journal-directory>data/journal</journal-directory>

      <large-messages-directory>data/large-messages</large-messages-directory>

      <journal-datasync>true</journal-datasync>

      <journal-min-files>2</journal-min-files>

      <journal-pool-files>{journal_pool_files}</journal-pool-files>

      <journal-file-size>10M</journal-file-size>

      <!--
       This value was determined through a calculation.
       Your system could perform 0.28 writes per millisecond
       on the current journal configuration.
       That translates as a sync write every 3580000 nanoseconds.

       Note: If you specify 0 the system will perform writes directly to the disk.
             We recommend this to be 0 if you are using journalType=MAPPED and journal-datasync=false.
      -->
      <journal-buffer-timeout>3580000</journal-buffer-timeout>


      <!--
        When using ASYNCIO, this will determine the writing queue depth for libaio.
       -->
      <journal-max-io>1</journal-max-io>
      <!--
        You can verify the network health of a particular NIC by specifying the <network-check-NIC> element.
         <network-check-NIC>theNicName</network-check-NIC>
        -->

      <!--
        Use this to use an HTTP server to validate the network
         <network-check-URL-list>http://www.apache.org</network-check-URL-list> -->

      <!-- <network-check-period>10000</network-check-period> -->
      <!-- <network-check-timeout>1000</network-check-timeout> -->

      <!-- this is a comma separated list, no spaces, just DNS or IPs
           it should accept IPV6

           Warning: Make sure you understand your network topology as this is meant to validate if your network is valid.
                    Using IPs that could eventually disappear or be partially visible may defeat the purpose.
                    You can use a list of multiple IPs, and if any successful ping will make the server OK to continue running -->
      <!-- <network-check-list>10.0.0.1</network-check-list> -->

      <!-- use this to customize the ping used for ipv4 addresses -->
      <!-- <network-check-ping-command>ping -c 1 -t %d %s</network-check-ping-command> -->

      <!-- use this to customize the ping used for ipv6 addresses -->
      <!-- <network-check-ping6-command>ping6 -c 1 %2$s</network-check-ping6-command> -->




      <!-- how often we are looking for how many bytes are being used on the disk in ms -->
      <disk-scan-period>5000</disk-scan-period>

      <!-- once the disk hits this limit the system will block, or close the connection in certain protocols
           that won't support flow control. -->
      <max-disk-usage>90</max-disk-usage>

      <!-- should the broker detect dead locks and other issues -->
      <critical-analyzer>true</critical-analyzer>

      <critical-analyzer-timeout>120000</critical-analyzer-timeout>

      <critical-analyzer-check-period>60000</critical-analyzer-check-period>

      <critical-analyzer-policy>HALT</critical-analyzer-policy>

      <!-- the system will enter into page mode once you hit this limit.
           This is an estimate in bytes of how much the messages are using in memory

            The system will use half of the available memory (-Xmx) by default for the global-max-size.
            You may specify a different value here if you need to customize it to your needs.

            <global-max-size>100Mb</global-max-size>

      -->

      <acceptors>

         <!-- useEpoll means: it will use Netty epoll if you are on a system (Linux) that supports it -->
         <!-- amqpCredits: The number of credits sent to AMQP producers -->
         <!-- amqpLowCredits: The server will send the # credits specified at amqpCredits at this low mark -->

         <!-- Note: If an acceptor needs to be compatible with HornetQ and/or Artemis 1.x clients add
                    "anycastPrefix=jms.queue.;multicastPrefix=jms.topic." to the acceptor url.
                    See https://issues.apache.org/jira/browse/ARTEMIS-1644 for more information. -->

         <!-- Acceptor for every supported protocol -->
         <acceptor name="artemis">tcp://0.0.0.0:61616?tcpSendBufferSize=1048576;tcpReceiveBufferSize=1048576;protocols=CORE,AMQP,STOMP,HORNETQ,MQTT,OPENWIRE;useEpoll=true;amqpCredits=1000;amqpLowCredits=300</acceptor>

         <!-- AMQP Acceptor.  Listens on default AMQP port for AMQP traffic.-->
         <acceptor name="amqp">tcp://0.0.0.0:5672?tcpSendBufferSize=1048576;tcpReceiveBufferSize=1048576;protocols=AMQP;useEpoll=true;amqpCredits=1000;amqpLowCredits=300</acceptor>

         <!-- STOMP Acceptor. -->
         <acceptor name="stomp">tcp://0.0.0.0:61613?tcpSendBufferSize=1048576;tcpReceiveBufferSize=1048576;protocols=STOMP;useEpoll=true</acceptor>

         <!-- HornetQ Compatibility Acceptor.  Enables HornetQ Core and STOMP for legacy HornetQ clients. -->
         <acceptor name="hornetq">tcp://0.0.0.0:5445?anycastPrefix=jms.queue.;multicastPrefix=jms.topic.;protocols=HORNETQ,STOMP;useEpoll=true</acceptor>

         <!-- MQTT Acceptor -->
         <acceptor name="mqtt">tcp://0.0.0.0:1883?tcpSendBufferSize=1048576;tcpReceiveBufferSize=1048576;protocols=MQTT;useEpoll=true</acceptor>

      </acceptors>


      <security-settings>
         <security-setting match="#">
            <permission type="createNonDurableQueue" roles="amq"/>
            <permission type="deleteNonDurableQueue" roles="amq"/>
            <permission type="createDurableQueue" roles="amq"/>
            <permission type="deleteDurableQueue" roles="amq"/>
            <permission type="createAddress" roles="amq"/>
            <permission type="deleteAddress" roles="amq"/>
            <permission type="consume" roles="amq"/>
            <permission type="browse" roles="amq"/>
            <permission type="send" roles="amq"/>
            <!-- we need this otherwise ./artemis data imp wouldn't work -->
            <permission type="manage" roles="amq"/>
         </security-setting>
      </security-settings>

      <address-settings>
         <!-- if you define auto-create on certain queues, management has to be auto-create -->
         <address-setting match="activemq.management#">
            <dead-letter-address>DLQ</dead-letter-address>
            <expiry-address>ExpiryQueue</expiry-address>
            <redelivery-delay>0</redelivery-delay>
            <!-- with -1 only the global-max-size is in use for limiting -->
            <max-size-bytes>-1</max-size-bytes>
            <message-counter-history-day-limit>10</message-counter-history-day-limit>
            <address-full-policy>PAGE</address-full-policy>
            <auto-create-queues>true</auto-create-queues>
            <auto-create-addresses>true</auto-create-addresses>
            <auto-create-jms-queues>true</auto-create-jms-queues>
            <auto-create-jms-topics>true</auto-create-jms-topics>
         </address-setting>
         <!--default for catch all-->
         <address-setting match="#">
            <dead-letter-address>DLQ</dead-letter-address>
            <expiry-address>ExpiryQueue</expiry-address>
            <redelivery-delay>0</redelivery-delay>
            <!-- with -1 only the global-max-size is in use for limiting -->
            <max-size-bytes>-1</max-size-bytes>
            <message-counter-history-day-limit>10</message-counter-history-day-limit>
            <address-full-policy>PAGE</address-full-policy>
            <auto-create-queues>true</auto-create-queues>
            <auto-create-addresses>true</auto-create-addresses>
            <auto-create-jms-queues>true</auto-create-jms-queues>
            <auto-create-jms-topics>true</auto-create-jms-topics>
         </address-setting>
      </address-settings>

      <addresses>
         <address name="DLQ">
            <anycast>
               <queue name="DLQ" />
            </anycast>
         </address>
         <address name="ExpiryQueue">
            <anycast>
               <queue name="ExpiryQueue" />
            </anycast>
         </address>

      </addresses>


      <!-- Uncomment the following if you want to use the Standard LoggingActiveMQServerPlugin pluging to log in events
      <broker-plugins>
         <broker-plugin class-name="org.apache.activemq.artemis.core.server.plugin.impl.LoggingActiveMQServerPlugin">
            <property key="LOG_ALL_EVENTS" value="true"/>
            <property key="LOG_CONNECTION_EVENTS" value="true"/>
            <property key="LOG_SESSION_EVENTS" value="true"/>
            <property key="LOG_CONSUMER_EVENTS" value="true"/>
            <property key="LOG_DELIVERING_EVENTS" value="true"/>
            <property key="LOG_SENDING_EVENTS" value="true"/>
            <property key="LOG_INTERNAL_EVENTS" value="true"/>
         </broker-plugin>
      </broker-plugins>
      -->

   </core>
</configuration>
"""


def test_parses():
    doc = AMQBroker(context_wrap(BROKER_DOT_XML.format(journal_pool_files=10)))
    assert doc.get_elements(".//journal-type", "urn:activemq:core")[0].text == "NIO"


def test_can_get_journal_pool_files():
    doc = AMQBroker(context_wrap(BROKER_DOT_XML.format(journal_pool_files=10)))
    assert int(doc.get_elements(".//journal-pool-files", "urn:activemq:core")[0].text) == 10


def test_can_get_negative_journal_pool_files():
    doc = AMQBroker(context_wrap(BROKER_DOT_XML.format(journal_pool_files=-1)))
    assert int(doc.get_elements(".//journal-pool-files", "urn:activemq:core")[0].text) == -1


def test_non_int_journal_pool_files():
    doc = AMQBroker(context_wrap(BROKER_DOT_XML.format(journal_pool_files="not_a_number")))
    with pytest.raises(ValueError):
        int(doc.get_elements(".//journal-pool-files", "urn:activemq:core")[0].text)
