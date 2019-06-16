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
dirsrv_sysconfig - file ``/etc/sysconfig/dirsrv``
=================================================

This module provides the ``DirsrvSysconfig`` class parser, for reading the
options in the ``/etc/sysconfig/dirsrv`` file.

Sample input::

    # how many seconds to wait for the startpid file to show
    # up before we assume there is a problem and fail to start
    # if using systemd, omit the "; export VARNAME" at the end
    #STARTPID_TIME=10 ; export STARTPID_TIME
    # how many seconds to wait for the pid file to show
    # up before we assume there is a problem and fail to start
    # if using systemd, omit the "; export VARNAME" at the end
    #PID_TIME=600 ; export PID_TIME
    KRB5CCNAME=/tmp/krb5cc_995
    KRB5_KTNAME=/etc/dirsrv/ds.keytab

Examples:

    >>> dirsrv_conf = shared[DirsrvSysconfig]
    >>> dirsrv.KRB5_KTNAME
    '/etc/dirsrv/ds.keytab'
    >>> 'PID_TIME' in dirsrv.data
    False

"""
from insights.util import deprecated
from .. import parser, SysconfigOptions
from insights.specs import Specs


@parser(Specs.dirsrv)
class DirsrvSysconfig(SysconfigOptions):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.DirsrvSysconfig` instead.

    Parse the `dirsrv` service's start-up configuration.
    """
    def __init__(self, *args, **kwargs):
        deprecated(DirsrvSysconfig, "Import DirsrvSysconfig from insights.parsers.sysconfig instead")
        super(DirsrvSysconfig, self).__init__(*args, **kwargs)

    set_properties = True
