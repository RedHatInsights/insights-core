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

'''
NetConsole - file ``/etc/sysconfig/netconsole``
===============================================

This parser reads the ``/etc/sysconfig/netconsole`` file.  It uses the
``SysconfigOptions`` parser class to convert the file into a dictionary of
options.

Sample data::

    # This is the configuration file for the netconsole service.  By starting
    # this service you allow a remote syslog daemon to record console output
    # from this system.

    # The local port number that the netconsole module will use
    LOCALPORT=6666


Examples:

    >>> config = shared[NetConsole]
    >>> 'LOCALPORT' in config.data
    True
    >>> 'DEV' in config # Direct access to options
    False

'''
from insights.util import deprecated
from .. import parser, SysconfigOptions, LegacyItemAccess
from insights.specs import Specs


@parser(Specs.netconsole)
class NetConsole(SysconfigOptions, LegacyItemAccess):
    '''
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.sysconfig.NetconsoleSysconfig` instead.

    Contents of the ``/etc/sysconfig/netconsole`` file.  Uses the
    ``SysconfigOptions`` shared parser class.
    '''
    def __init__(self, *args, **kwargs):
        deprecated(NetConsole, "Import NetconsoleSysconfig from insights.parsers.sysconfig instead")
        super(NetConsole, self).__init__(*args, **kwargs)
