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

from insights import Parser, parser
from insights.specs import Specs
from insights.parsers import ParseException, SkipException


@parser(Specs.bond_dynamic_lb)
class BondDynamicLB(Parser):
    """
    Models the ``/sys/class/net/bond[0-9]*/bonding/tlb_dynamic_lb`` file.

    0 - Hash based load balancing.

    1 - Load based load balancing.

    Raises:
        SkipException: When contents are empty
        ParseException: When contents are invalid
    """

    def parse_content(self, content):
        if not content:
            raise SkipException("No Contents")
        line = content[0].strip()
        self._dynamic_lb_status = None
        self._bond_name = self.file_path.rsplit("/")[-3]

        if line in ['0', '1']:
            self._dynamic_lb_status = int(line)
        else:
            raise ParseException("Unrecognised Values '{b}'".format(b=line))

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
