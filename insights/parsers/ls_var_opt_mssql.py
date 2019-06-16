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
LsDVarOptMSSql - command ``ls -ld /var/opt/mssql``
==================================================
"""
from insights.specs import Specs
from .. import CommandParser, parser, FileListing


@parser(Specs.ls_var_opt_mssql)
class LsDVarOptMSSql(CommandParser, FileListing):
    """Parses output of ``ls -ld /var/opt/mssql`` command.

    The ``ls -ld /var/opt/mssql`` command provides information for the listing
    of the ``/var/opt/mssql`` directory. See ``FileListing`` class for addtional
    information.


    Sample ``ls -ld /var/opt/mssql`` output::

        drwxrwx---. 5 root root 58 Apr 16 07:20 /var/opt/mssql

    Examples:

        >>> content.listing_of('/var/opt/mssql').get('/var/opt/mssql').get('owner')
        'root'
        >>> content.listing_of('/var/opt/mssql').get('/var/opt/mssql').get('group')
        'root'
    """
    pass
