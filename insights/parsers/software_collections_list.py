"""
Software Collections list output - command ``scl --list`` RHEL-6/7
==================================================================

This module provides parser for list output of ``scl``. This spec
is valid for ``RHEL-6/7`` only, ``-l|--list`` is ``deprecated`` in
``RHEL-8``. On ``RHEL-8`` same functionality can be achieved by
``scl list-collections`` spec.

Parser provided by this module is:

SoftwareCollectionsListInstalled - command ``scl --list``
---------------------------------------------------------

"""

from insights import CommandParser, parser
from insights.parsers import get_active_lines
from insights.specs import Specs
from insights.components.rhel_version import IsRhel6, IsRhel7


@parser(Specs.software_collections_list, [IsRhel6, IsRhel7])
class SoftwareCollectionsListInstalled(CommandParser):
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
