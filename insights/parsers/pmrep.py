"""
Pmrep - command ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv``
=====================================================================================================================

Parse the content of the ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv`` command.

Sample ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv`` command output::

    Time,"network.interface.out.packets-lo","network.interface.out.packets-eth0","network.interface.collisions-lo","network.interface.collisions-eth0","swap.pagesout"
    2021-04-26 05:42:24,,,,,
    2021-04-26 05:42:25,1.000,2.000,3.000,4.000,5.000

Examples:
    >>> type(pmrep_doc_obj)
    <class 'insights.parsers.pmrep.PMREPMetrics'>
    >>> pmrep_doc_obj[1]
    {'network.interface.out.packets-lo': '1.000'}
    >>> pmrep_doc_obj[4]
    {'network.interface.collisions-eth0': '4.000'}
    >>> pmrep_doc_obj[5]
    {'swap.pagesout': '5.000'}
"""

import os
from csv import DictReader

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.pmrep_metrics)
class PMREPMetrics(CommandParser, list):
    """Parses output of ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv`` command."""
    def parse_content(self, content):
        temp = {}
        if not content or len(content) == 1:
            raise SkipException("There is no data in the table")
        try:
            reader = DictReader(os.linesep.join(content).splitlines(True))
        except Exception:
            raise ParseException("The content isn't in csv format")
        for row in reader:
            # check the "swap.pagesout" metric value is empty, if the value is empty for this key, will be empty for the remaining keys except the "Time" key
            if row["swap.pagesout"]:
                for k, v in dict(row).items():
                    temp[k] = dict(row)[k]
                    self.append(temp)
                    temp = {}
