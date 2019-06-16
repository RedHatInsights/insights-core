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
