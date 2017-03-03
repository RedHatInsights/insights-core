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

import yaml
from .. import Mapper, mapper, LegacyItemAccess


@mapper('cobbler_settings')
class CobblerSettings(LegacyItemAccess, Mapper):
    """
    Read the ``/etc/cobbler/settings`` YAML file.
    """

    def parse_content(self, content):
        # Revert the list to a stream string
        self.data = yaml.load('\n'.join(content))
