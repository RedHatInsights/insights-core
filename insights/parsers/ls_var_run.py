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
LsVarRun - command ``ls -lnL /var/run``
=======================================

The ``ls -lnL /var/run`` command provides information for the listing of the
``/var/run`` directory.

Sample input is shown in the Examples. See ``FileListing`` class for
additional information.

Sample directory list::

    total 20
    drwx--x---.  2   0 984   40 May 15 09:29 openvpn
    drwxr-xr-x.  2   0   0   40 May 15 09:30 plymouth
    drwxr-xr-x.  2   0   0   40 May 15 09:29 ppp
    drwxr-xr-x.  2  75  75   40 May 15 09:29 radvd
    -rw-r--r--.  1   0   0    5 May 15 09:30 rhnsd.pid
    drwxr-xr-x.  2   0   0   60 May 30 09:31 rhsm
    drwx------.  2  32  32   40 May 15 09:29 rpcbind
    -r--r--r--.  1   0   0    0 May 17 16:26 rpcbind.lock

Examples:

    >>> "rhnsd.pid" in ls_var_run
    False
    >>> "/var/run" in ls_var_run
    True
    >>> ls_var_run.dir_entry('/var/run', 'openvpn')['type']
    'd'
"""


from insights.specs import Specs

from .. import FileListing
from .. import parser


@parser(Specs.ls_var_run)
class LsVarRun(FileListing):
    """Parses output of ``ls -lnL /var/run`` command."""
    pass
