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
LsVarTmp - command ``ls -ln /var/tmp``
======================================

The ``ls -ln /var/tmp`` command provides information for the listing of the
``/var/tmp`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    /var/tmp:
    total 20
    drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a1
    drwxr-xr-x.  2 0 0 4096 Mar 26 02:25 a2
    drwxr-xr-x.  2 0 0 4096 Apr 28  2018 foreman-ssh-cmd-fc3f65c9-2b35-480d-87e3-1d971433d6ad

Examples:

    >>> "a1" in ls_var_tmp
    False
    >>> "/var/tmp" in ls_var_tmp
    True
    >>> ls_var_tmp.dir_entry('/var/tmp', 'a1')['type']
    'd'
"""


from insights.specs import Specs
from insights.core.filters import add_filter

from .. import FileListing
from .. import parser, CommandParser


add_filter(Specs.ls_var_tmp, "/var/tmp")


@parser(Specs.ls_var_tmp)
class LsVarTmp(CommandParser, FileListing):
    """Parses output of ``ls -ln /var/tmp`` command."""
    pass
