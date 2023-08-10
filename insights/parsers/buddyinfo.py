"""
buddyinfo - file ``/proc/buddyinfo``
====================================

This parsers the contents of ``/proc/buddyinfo``.

Here is from the mannual page of ``/proc/buddyinfo``:

    /proc/buddyinfo
            This file contains information which is used for
            diagnosing memory fragmentation issues.  Each line starts
            with the identification of the node and the name of the
            zone which together identify a memory region.  This is
            then followed by the count of available chunks of a
            certain order in which these zones are split.  The size in
            bytes of a certain order is given by the formula:

                (2^order) * PAGE_SIZE

            The binary buddy allocator algorithm inside the kernel
            will split one chunk into two chunks of a smaller order
            (thus with half the size) or combine two contiguous chunks
            into one larger chunk of a higher order (thus with double
            the size) to satisfy allocation requests and to counter
            memory fragmentation.  The order matches the column
            number, when starting to count at zero.

            If the memory is heavily fragmented, the counters for
            higher order chunks will be zero and allocation of large
            contiguous areas will fail.

This parser will only store the counter of memory fragmentation.
To get the real size of each column, use ``PAGE_SIZE`` from parser
class:``GetconfPageSize`` for calculation.

For each line in ``/proc/buddyinfo``, it will be parsed and stored in a dict
with the following properties:

* ``node`` (str)     - the Node ID, eg. "0"
* ``zone`` (str)     - the zone name, eg. "Normal"
* ``counter`` (list) - the chuck numbers in order
* ``raw`` (str)      - the raw line

Sample data::

    Node 0, zone      DMA      0      0      0      0      0      0      0      0      1      1      2
    Node 0, zone    DMA32      8     10     12      9      9     11     10     12     12     11    569
    Node 0, zone   Normal    460    485    375   1611   3201   2187   1437    844    487    247   6120
    Node 1, zone   Normal      1      7   1783   2063   1773   3227   2299   1399    729    430   6723

Examples:

    >>> len(buddy)
    4
    >>> mem = buddy[2]
    >>> mem['node']
    '0'
    >>> mem['zone']
    'Normal'
    >>> mem['counter']
    [460, 485, 375, 1611, 3201, 2187, 1437, 844, 487, 247, 6120]
    >>> mem['counter'][0]   # (2^0) * PAGE_SIZE (order 0)
    460
    >>> mem['counter'][10]  # (2^10) * PAGE_SIZE (order 10)
    6120
    >>> mem['raw']
    'Node 0, zone   Normal    460    485    375   1611   3201   2187   1437    844    487    247   6120'
"""

from insights.core import Parser
from insights.core.plugins import parser
from insights.core.exceptions import SkipComponent
from insights.specs import Specs


@parser(Specs.buddyinfo)
class BuddyInfo(Parser, list):
    """Prase the contents of ``/proc/buddyinfo``."""

    def parse_content(self, content):
        for line in content:
            node_str, other_str = line.split(',', 1)
            others = other_str.split()
            self.append({
                'node': node_str.split()[-1],
                'zone': others[1],
                'counter': [int(v) for v in others[2:]],
                'raw': line,
            })

        if len(self) < 1:
            raise SkipComponent
