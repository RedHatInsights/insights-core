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
Cobbler settings - ``/etc/cobbler/settings`` file
=================================================

The Cobbler settings file is a **YAML** file and the standard Python ``yaml``
library is used to parse it.

Sample input::

    kernel_options:
        ksdevice: bootif
        lang: ' '
        text: ~

Examples:

    >>> cobbler = shared[CobblerSettings]
    >>> 'kernel_options' in cobbler.data
    True
    >>> cobbler.data['kernel_options']['ksdevice']
    'bootif'

"""

from .. import YAMLParser, parser
from insights.specs import Specs


@parser(Specs.cobbler_settings)
class CobblerSettings(YAMLParser):
    """
    Read the ``/etc/cobbler/settings`` YAML file.
    """
    pass
