"""
SendQSocketBuffer - file ``/proc/sys/net/ipv4/tcp_wmem``
--------------------------------------------------------
RecvQSocketBuffer - file ``/proc/sys/net/ipv4/tcp_rmem``
--------------------------------------------------------
"""
from insights.core import Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs


class SocketBuffer(Parser):
    """ Base class for SendQSocketBuffer & RecvQSocketBuffer
    """
    def parse_content(self, content):
        if not content:
            raise ParseException("Empty content")
        buffer_values = content[-1].split()
        self.raw = " ".join(buffer_values)
        self.minimum, self.default, self.maximum = [int(value) for value in buffer_values]

    def __repr__(self):
        return "<raw: {r}, minimum: {min}, default: {dft}, maximum: {max}>".format(
            r=self.raw,
            min=self.minimum,
            dft=self.default,
            max=self.maximum
        )


@parser(Specs.sendq_socket_buffer)
class SendQSocketBuffer(SocketBuffer):
    """Parse the file ``/proc/sys/net/ipv4/tcp_wmem``

    Parameter ipv4/tcp_wmem is the amount of memory in bytes write (transmit) buffer per open socket.
    This is a vector of 3 integers: [min, default, max].
    These parameters are used by TCP to regulate send buffer sizes.
    TCP dynamically adjusts the size of the send buffer from the default values listed below,
    in the range of these values, depending on memory available.

    Read more on http://man7.org/linux/man-pages/man7/tcp.7.html

    Sample input::
        4096	16384	4194304

    Examples:
        >>> sendq_buffer_values.raw
        '4096 16384 4194304'
        >>> sendq_buffer_values.minimum
        4096
        >>> sendq_buffer_values.default
        16384
        >>> sendq_buffer_values.maximum
        4194304

    Attributes:
        raw: The raw content of send buffer sizes from tcp_wmem
        minimum: Minimum size of the send buffer used by each TCP socket
        default: The default size of the send buffer for a TCP socket
        maximum: The maximum size of the send buffer used by each TCP socket
    """
    pass


@parser(Specs.recvq_socket_buffer)
class RecvQSocketBuffer(SocketBuffer):
    """Parse the file ``/proc/sys/net/ipv4/tcp_rmem``

    Parameter ipv4/tcp_rmem is the amount of memory in bytes for read (receive) buffer per open socket.
    This is a vector of 3 integers: [min, default, max].
    These parameters are used by TCP to regulate receive buffer sizes.
    TCP dynamically adjusts the size of the receive buffer from the defaults listed below,
    in the range of these values, depending on memory available in the system.

    Read more on http://man7.org/linux/man-pages/man7/tcp.7.html

    Sample input::
        4096	87380	6291456

    Examples:
        >>> recvq_buffer_values.raw
        '4096 87380 6291456'
        >>> recvq_buffer_values.minimum
        4096
        >>> recvq_buffer_values.default
        87380
        >>> recvq_buffer_values.maximum
        6291456

    Attributes:
        raw: The raw content of receive buffer sizes from tcp_rmem
        minimum: Minimum size of the receive buffer used by each TCP socket
        default: The default size of the receive buffer for a TCP socket
        maximum: The maximum size of the receive buffer used by each TCP socket
    """
    pass
