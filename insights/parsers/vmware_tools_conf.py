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
VMwareToolsConf - file ``/etc/vmware-tools/tools.conf``
=======================================================

The VMware tools configuration file ``/etc/vmware-tools/tools.conf``
is in the standard 'ini' format and is read by the IniConfigFile
parser. ``vmtoolsd.service`` provided by ``open-vm-tools`` package is
configured using ``/etc/vmware-tools/tools.conf``.


Sample ``/etc/vmware-tools/tools.conf`` file::

    [guestinfo]
    disable-query-diskinfo = true

    [logging]
    log = true

    vmtoolsd.level = debug
    vmtoolsd.handler = file
    vmtoolsd.data = /tmp/vmtoolsd.log


Examples:

    >>> list(conf.sections()) == [u'guestinfo', u'logging']
    True
    >>> conf.has_option('guestinfo', 'disable-query-diskinfo')
    True
    >>> conf.getboolean('guestinfo', 'disable-query-diskinfo')
    True
    >>> conf.get('guestinfo', 'disable-query-diskinfo') == u'true'
    True

"""
from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.vmware_tools_conf)
class VMwareToolsConf(IniConfigFile):
    """Class for VMware tool configuration file content."""
    pass
