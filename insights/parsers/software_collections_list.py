"""
Software Collections list output - command ``scl --list``
=========================================================================

This module provides parser for list output of ``scl``.

Parser provided by this module is:

SoftwareCollectionsListInstalled - command ``scl --list``
------------------------------------------------------------------------------------

"""

from .. import Parser, parser
from . import get_active_lines
from insights.specs import Specs


@parser(Specs.software_collections_list)
class SoftwareCollectionsListInstalled(Parser):
    """
    An object for parsing the output of ``scl --list``.

    Sample input file::

        devtoolset-7
        httpd24
        python27
        rh-mysql57
        rh-nodejs8
        rh-php71
        rh-python36
        rh-ruby24

    Examples:
        >>> type(collections)
        <class 'insights.parsers.software_collections_list.SoftwareCollectionsListInstalled'>
        >>> len(collections.records)
        8
        >>> coll1 = collections.records[0]
        >>> coll1
        'devtoolset-7'
        >>> coll2 = collections.records[4]
        >>> coll2
        'rh-nodejs8'
        >>> collections.exists('rh-ruby24')
        True
        >>> collections.exists('rh-missing_colection')
        False

    """
    def parse_content(self, content):
        self.records = []
        for line in get_active_lines(content):
            self.records.append(line)

    def exists(self, collection_name):
        """
        Checks if the collection is installed on the system.

        Args:
           service_name (str): collections name

        Returns:
            bool: True if collections exists, False otherwise.
        """
        return collection_name in self.records
