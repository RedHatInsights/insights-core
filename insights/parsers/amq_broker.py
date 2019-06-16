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

"""
AMQBroker - file ``/var/opt/amq-broker/*/etc/broker.xml``
=========================================================

Configuration of Active MQ Artemis brokers.
"""
from .. import XMLParser, parser
from insights.specs import Specs


@parser(Specs.amq_broker)
class AMQBroker(XMLParser):
    """
    Provides access to broker.xml files that are stored in the conventional
    location for Active MQ Artemis.

    Examples:
        >>> doc.get_elements(".//journal-pool-files", "urn:activemq:core")[0].text
        "10"
        >>> doc.get_elements(".//journal-type", "urn:activemq:core")[0].text
        "NIO"
    """
    pass
