"""
Pmrep - command ``pmrep -t 1s -T 1s <metrics> -o csv``
======================================================

Parse the content of the ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout mssql.memory_manager.stolen_server_memory mssql.memory_manager.total_server_memory -o csv`` command.

Sample ``pmrep -t 1s -T 1s network.interface.out.packets network.interface.collisions swap.pagesout -o csv`` command output::

    Time,"network.interface.out.packets-lo","network.interface.out.packets-eth0","network.interface.collisions-lo","network.interface.collisions-eth0","swap.pagesout"
    2021-04-26 05:42:24,,,,,
    2021-04-26 05:42:25,1.000,2.000,3.000,4.000,5.000

Examples:
    >>> type(pmrep_doc_obj)
    <class 'insights.parsers.pmrep.PMREPMetrics'>
    >>> pmrep_doc_obj = sorted(pmrep_doc_obj, key=lambda x: x['name'])
    >>> pmrep_doc_obj[3]
    {'name': 'network.interface.collisions-eth0', 'value': '4.000'}
    >>> pmrep_doc_obj[6]
    {'name': 'network.interface.out.packets-lo', 'value': '1.000'}
    >>> pmrep_doc_obj[7]
    {'name': 'swap.pagesout', 'value': '5.000'}
"""

from csv import DictReader
from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException, keyword_search


@parser(Specs.pmrep_metrics)
class PMREPMetrics(CommandParser, list):
    """Parses output of ``pmrep -t 1s -T 1s <metrics> -o csv`` command."""
    def parse_content(self, content):
        if not content or len(content) == 1:
            raise SkipException("There is no data in the table")
        try:
            reader = DictReader(content)
        except Exception:
            raise ParseException("The content isn't in csv format")
        for k, v in dict(list(reader)[-1]).items():
            self.append(dict(name=k, value=v))

    def search(self, **kwargs):
        """
        Get the rows by searching the table with kwargs.
        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details. If no search
        parameters are given, no rows are returned.

        Returns:
            list: A list of dictionaries of rows that match the given
            search criteria.

        Examples:
            >>> sorted(pmrep_doc_obj_search.search(name__endswith='lo'), key=lambda x: x['name'])
            [{'name': 'network.interface.collisions-lo', 'value': '3.000'}, {'name': 'network.interface.out.packets-lo', 'value': '1.000'}]
            >>> sorted(pmrep_doc_obj_search.search(name__endswith='swap.pagesout'), key=lambda x: x['name'])
            [{'name': 'swap.pagesout', 'value': '5.000'}]
        """
        return keyword_search(self, **kwargs)
