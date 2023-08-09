"""
NfnetLinkQueue - file ``/proc/net/netfilter/nfnetlink_queue``
=============================================================
"""
from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.nfnetlink_queue)
class NfnetLinkQueue(Parser, list):
    """
    Reads the ``/proc/net/netfilter/nfnetlink_queue`` file and creates a list of
    dictionaries, one dictionary per row in the file.

    The keys of the dictionary are (see
    https://home.regit.org/netfilter-en/using-nfqueue-and-libnetfilter_queue/):

    - ``queue_number``
    - ``peer_portid``: good chance it is process ID of software listening to
      the queue
    - ``queue_total``: current number of packets waiting in the queue
    - ``copy_mode``: 0 and 1 only message only provide meta data. If 2, the
      message provides a part of packet of size copy range.
    - ``copy_range``: length of packet data to put in message
    - ``queue_dropped``: number of packets dropped because queue was full
    - ``user_dropped``: number of packets dropped because netlink message
      could not be sent to userspace. If this counter is not zero, try
      to increase netlink buffer size. On the application side, you will
      see gap in packet id if netlink message are lost.
    - ``id_sequence``: packet id of last packet
    - The last field is always '1' and is ignored.

    Example Input::

        0  -4423     0 2 65535     0     0       22  1
        1  -4424     0 2 65535     0     0       27  1

    Examples:

        >>> type(nf)
        <class 'insights.parsers.nfnetlink_queue.NfnetLinkQueue'>
        >>> 'copy_mode' in nf.data[0]
        True
        >>> nf.data[0]['copy_mode']
        2
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")

        data = []
        fields = ['queue_number', 'peer_portid', 'queue_total', 'copy_mode',
                  'copy_range', 'queue_dropped', 'user_dropped', 'id_sequence']

        for line in content:
            parts = [int(p.strip()) for p in line.split()]

            if len(parts) != 9:
                raise ParseException("Can't parse content because there isn't 9 columns provided.")

            data.append(dict(zip(fields, parts)))

        if not data:
            raise SkipComponent("No parsed data.")

        self.extend(data)

    @property
    def data(self):
        """
        Set data as property to keep compatibility
        """
        return self
