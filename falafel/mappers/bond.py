"""
Bond
====

Provides plugins access to the network bonding information gathered from
all the files starteing with "bond." located in the
``/proc/net/bonding`` directory.

Typical content of ``bond.*`` file is:

    Ethernet Channel Bonding Driver: v3.7.1 (April 27, 2011)

    Bonding Mode: load balancing (round-robin)
    MII Status: up
    MII Polling Interval (ms): 100
    Up Delay (ms): 0
    Down Delay (ms): 0

    Slave Interface: eno1
    MII Status: up
    Speed: 1000 Mbps
    Duplex: full
    Link Failure Count: 0
    Permanent HW addr: 2c:44:fd:80:5c:f8
    Slave queue ID: 0

    Slave Interface: eno2
    MII Status: up
    Speed: 1000 Mbps
    Duplex: full
    Link Failure Count: 0
    Permanent HW addr: 2c:44:fd:80:5c:f9
    Slave queue ID: 0

So, the data consists of stanzas of key value pairs.
"""
from falafel.core.plugins import mapper
from falafel.core import MapperOutput


class BondInfo(MapperOutput):

    def __contains__(self, s):
        """
        Check if the specified string 's' is contained in lspci output.
        """
        return any(s in line for line in self.data)

    def get(self, s):
        """
        Returns all lines that contain 's' and wrap them into a list
        """
        return [line for line in self.data if s in line]


@mapper('bond')
def bondinfo(context):
    return BondInfo(context.content, path=context.path)
