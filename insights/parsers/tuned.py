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
Tuned - command ``/usr/sbin/tuned-adm list``
============================================

This parser reads the output of the ``/usr/sbin/tuned-adm list`` command and
reads it into a simple dictionary in the ``data`` property with two of three
keys:

* ``available`` - the list of available profiles
* ``active`` - the active profile name
* ``preset`` - the profile name that's preset to be used when tuned is active

The ``active`` key is available when ``tuned`` is running, because the active
profile is only listed when the daemon is active.  If ``tuned`` is not
running, the tuned-adm command will list the profile that will be used when
the daemon is running, and this is given in the ``preset`` key.

Sample data::

    Available profiles:
    - balanced
    - desktop
    - latency-performance
    - network-latency
    - network-throughput
    - powersave
    - throughput-performance
    - virtual-guest
    - virtual-host
    Current active profile: virtual-guest

Examples:

    >>> result = shared[Tuned]
    >>> 'active' in result.data
    True
    >>> result.data['active']
    'virtual-guest'
    >>> len(result.data['available'])
    9
    >>> 'balanced' in result.data['available']
    True
"""

from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.tuned_adm)
class Tuned(CommandParser):
    """
    Parse data from the ``/usr/sbin/tuned-adm list`` command.
    """

    def parse_content(self, content):
        self.data = {}
        self.data['available'] = []
        for line in content:
            if line.startswith('-'):
                self.data['available'].append(line.split('- ')[1])
            elif line.startswith('Current'):
                self.data['active'] = line.split(': ')[1]
            elif line.startswith('Preset'):
                self.data['preset'] = line.split(': ')[1]
            # Ignore everything else for now
