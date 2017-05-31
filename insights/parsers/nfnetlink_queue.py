from .. import Parser, parser


@parser('nfnetlink_queue')
class NfnetLinkQueue(Parser):
    """Reads the ``/proc/net/netfilter/nfnetlink_queue`` file and
    creates a list of dictionaries, one dictionary per row in the file.

    The keys of the dictionary are (see
    https://home.regit.org/netfilter-en/using-nfqueue-and-libnetfilter_queue/):
    - queue_number
    - peer_portid: good chance it is process ID of software listening to
      the queue
    - queue_total: current number of packets waiting in the queue
    - copy_mode: 0 and 1 only message only provide meta data. If 2
      message provide a part of packet of size copy range.
    - copy_range: length of packet data to put in message
    - queue_dropped: number of packets dropped because queue was full
    - user_dropped: number of packets dropped because netlink message
      could not be sent to userspace. If this counter is not zero, try
      to increase netlink buffer size. On the application side, you will
      see gap in packet id if netlink message are lost.
    - id_sequence: packet id of last packet

    Example Input:

        0  -4423     0 2 65535     0     0       22  1
        1  -4424     0 2 65535     0     0       27  1

    Resulting Data Structure

       [{'queue_number': 0,
         'peer_portid': '-4423',
         'queue_total': 0,
         'copy_mode': 2,
         'copy_range': 65535,
         'queue_dropped': 0,
         'user_dropped': 0,
         'id_sequence': 22},
        {'queue_number': 1,
         'peer_portid': '-4424',
         'queue_total': 0,
         'copy_mode': 2,
         'copy_range': 65535,
         'queue_dropped': 0,
         'user_dropped': 0,
         'id_sequence': 27}
       ]

    """

    def parse_content(self, content):
        self.data = []
        for line in content:
            parts = [int(p.strip()) for p in line.split()]
            assert len(parts) == 9

            row = {'queue_number': parts[0],
                   'peer_portid': parts[1],
                   'queue_total': parts[2],
                   'copy_mode': parts[3],
                   'copy_range': parts[4],
                   'queue_dropped': parts[5],
                   'user_dropped': parts[6],
                   'id_sequence': parts[7]}
            self.data.append(row)
