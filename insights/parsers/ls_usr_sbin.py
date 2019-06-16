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
LsUsrSbin - command ``ls -ln /usr/sbin``
========================================

The ``ls -ln /usr/sbin`` command provides information for the listing of the
``/usr/sbin`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

For ls_usr_sbin, it may collect a lot of files or directories that may not be
necessary, so a default filter `add_filter(Specs.ls_usr_sbin, "total")` has
been added in this parser.

If addtional file or directory need to be collected by this parser, please
add related filter to corresponding code.

Sample added filter:

    >>> add_filter(Specs.ls_usr_sbin, "accessdb")

Sample directory list collected::

    total 41472
    -rwxr-xr-x. 1 0  0   11720 Mar 18  2014 accessdb

Examples:

    >>> "accessdb" in ls_usr_sbin
    False
    >>> "/usr/sbin" in ls_usr_sbin
    True
    >>> ls_usr_sbin.dir_entry('/usr/sbin', 'accessdb')['type']
    '-'

Sample added filter:

    >>> add_filter(Specs.ls_usr_sbin, "accessdb")
    >>> add_filter(Specs.ls_usr_sbin, "postdrop")

Sample directory list collected::

    total 41472
    -rwxr-xr-x. 1 0  0   11720 Mar 18  2014 accessdb
    -rwxr-sr-x. 1 0 90  218552 Jan 27  2014 postdrop

Examples:

    >>> "accessdb" in ls_usr_sbin
    False
    >>> "/usr/sbin" in ls_usr_sbin
    True
    >>> ls_usr_sbin.dir_entry('/usr/sbin', 'accessdb')['type']
    '-'
    >>> ls_usr_sbin.dir_entry('/usr/sbin', 'postdrop')['type']
    '-'
"""


from insights.core.filters import add_filter
from insights.specs import Specs

from .. import CommandParser, parser
from .. import FileListing


add_filter(Specs.ls_usr_sbin, "total")


@parser(Specs.ls_usr_sbin)
class LsUsrSbin(CommandParser, FileListing):
    """Parses output of ``ls -ln /usr/sbin`` command."""
    pass
