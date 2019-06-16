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
DnfModules - files under in the ``/etc/dnf/modules.d/`` directory
=================================================================

Modularity configuration
"""
from insights import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.dnf_modules)
class DnfModules(IniConfigFile):
    """
    Provides access to state of enabled modules/streams/profiles
    which is located in the /etc/dnf/modules.d/ directory

    Examples:
        >>> len(dnf_modules.sections())
        3
        >>> str(dnf_modules.get("postgresql", "stream"))
        '9.6'
        >>> str(dnf_modules.get("postgresql", "profiles"))
        'client'
    """
    pass
