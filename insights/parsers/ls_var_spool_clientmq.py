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
LsVarSpoolClientmq - command ``ls -ln /var/spool/clientmqueue``
===============================================================

The ``ls -ln /var/spool/clientmqueue`` command provides information for the listing of the ``/var/spool/clientmqueue`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 40
    -rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6Wilr002718
    -rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6WixJ002715
    -rw-rw---- 1 51 51   4 Jul 11 02:32 dfw6B6WjP6002721
    -rw-rw---- 1 51 51 817 Jul 11 03:35 dfw6B7Z8BB002906
    -rw-rw---- 1 51 51 817 Jul 11 04:02 dfw6B822T0011150

Examples:

    >>> "dfw6B6Wilr002718" in ls_var_spool_clientmq
    False
    >>> "/var/spool/clientmqueue" in ls_var_spool_clientmq
    True
    >>> ls_var_spool_clientmq.dir_entry('/var/spool/clientmqueue', 'dfw6B6Wilr002718')['type']
    '-'
"""


from insights.specs import Specs

from .. import CommandParser, parser
from .. import FileListing


@parser(Specs.ls_var_spool_clientmq)
class LsVarSpoolClientmq(CommandParser, FileListing):
    """Parses output of ``ls -ln /var/spool/clientmqueue`` command."""
    pass
