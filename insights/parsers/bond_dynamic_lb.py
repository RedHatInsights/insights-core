"""
BondDynamicLB - file ``/sys/class/net/bond[0-9]*/bonding/tlb_dynamic_lb``
=========================================================================

This file represent weather the transmit load balancing is enabled or not

tlb_dynamic_lb=1 mode:
    The outgoing traffic is distributed according to the current load.

tlb_dynamic_lb=0 mode:
    The load balancing based on current load is disabled and the load
    is distributed only using the hash distribution.

Typical content of the file is::

        1

Data is modeled as an array of ``BondDynamicLB`` objects

Examples:
    >>> type(tlb_bond)
    <class 'insights.parsers.bond_dynamic_lb.BondDynamicLB'>
    >>> tlb_bond.dynamic_lb_status
    1
    >>> tlb_bond.bond_name
    'bond0'
"""

from insights import Parser, parser, get_active_lines
from insights.specs import Specs


@parser(Specs.bond_dynamic_lb)
class BondDynamicLB(Parser):
    """
    Models the ``/sys/class/net/bond[0-9]*/bonding/tlb_dynamic_lb`` file.

    0 - Hash based load balancing.

    1 - Load based load balancing.
    """

    def __init__(self, context):
        super(BondDynamicLB, self).__init__(context)
        self._bond_name = context.path.rsplit("/")[-3]

    def parse_content(self, content):
        self._dynamic_lb_status = None
        for line in get_active_lines(content):
            if line in ['0', '1']:
                self._dynamic_lb_status = int(line)

    @property
    def dynamic_lb_status(self):
        """
        Returns (int): Load balancer type
        """
        return self._dynamic_lb_status

    @property
    def bond_name(self):
        """
        Returns (str): Name of bonding interface
        """
        return self._bond_name
