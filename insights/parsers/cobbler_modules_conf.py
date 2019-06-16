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
Cobbler modules configuration - file ``/etc/cobbler/modules.conf``
==================================================================

The Cobbler modules configuration lists a set of services, and typically
sets the module that provides that service.

Sample input::

    [authentication]
    module = authn_spacewalk

    [authorization]
    module = authz_allowall

    [dns]
    module = manage_bind

    [dhcp]
    module = manage_isc

Examples:

    >>> conf = CobblerModulesConf(context_wrap(conf_content))
    >>> conf.get('authentication', 'module')
    'authn_spacewalk'
    >>> conf.get('dhcp', 'module')
    'manage_isc'

"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.cobbler_modules_conf)
class CobblerModulesConf(IniConfigFile):
    """
    This uses the standard ``IniConfigFile`` parser class.
    """
    pass
