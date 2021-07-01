"""
CandlepinBrokerXML - file ``/etc/candlepin/broker.xml``
=======================================================
"""

from insights.core import XMLParser
from insights import parser
from insights.specs import Specs


@parser(Specs.candlepin_broker)
class CandlepinBrokerXML(XMLParser):
    """
    Parse the ``/etc/candlepin/broker.xml`` file.

    .. note::
        Please refer to its super-class :class:`insights.core.XMLParser`

    Examples:
        >>> type(broker)
        <class 'insights.parsers.candlepin_broker.CandlepinBrokerXML'>
        >>> page_dirs = broker.get_elements('.//paging-directory')
        >>> page_dirs[0].text
        '/var/lib/candlepin/activemq-artemis/paging'
        >>> usage_ele = broker.dom.find('.//max-disk-usage')
        >>> usage_ele.text
        '99'
    """
    pass
