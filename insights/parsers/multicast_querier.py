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
MulticastQuerier - command ``find /sys/devices/virtual/net/ -name multicast_querier -print -exec cat {} \;``
============================================================================================================

This module provides processing for the output of the
``find -name multicast_querier ...`` command.

Sample output of this command looks like::

    /sys/devices/virtual/net/br0/bridge/multicast_querier
    0
    /sys/devices/virtual/net/br1/bridge/multicast_querier
    1
    /sys/devices/virtual/net/br2/bridge/multicast_querier
    0

The ``bri_val`` method is to return a dictionary contains bridge interface and
its multicast_querier value as the parsing result::

{'br0': 0, 'br1': 1, 'br2': 0}

Examples:
    >>> multicast_querier_content = '''
    ... /sys/devices/virtual/net/br0/bridge/multicast_querier
    ... 0
    ... /sys/devices/virtual/net/br1/bridge/multicast_querier
    ... 1
    ... /sys/devices/virtual/net/br2/bridge/multicast_querier
    ... 0
    ... '''.strip()
    >>> from insights.tests import context_wrap
    >>> from insights.parsers.multicast_querier import MulticastQuerier
    >>> shared = {MulticastQuerier: MulticastQuerier(context_wrap(multicast_querier_content))}
    >>> mq_results = MulticastQuerier(context_wrap(multicast_querier_content))
    >>> mq_results.bri_val
    {'br0': 0, 'br1': 1, 'br2': 0}
"""

from .. import parser, CommandParser
from insights.specs import Specs


@parser(Specs.multicast_querier)
class MulticastQuerier(CommandParser):
    """
    Parse the output of the command:

    `find /sys/devices/virtual/net/ -name multicast_querier -print -exec cat {} \;`

    Get a dictionary of "bridge interface" and the value of the parameter "multicast_querier"
    """
    @property
    def bri_val(self):
        return self._mapping

    def parse_content(self, content):
        self._mapping = {}
        for line in content:
            mq_val = ''
            if line.startswith('/sys/'):
                bri_iface = line.split('/')[5]
            else:
                mq_val = int(line.strip())
            self._mapping[bri_iface] = mq_val
        return
