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
