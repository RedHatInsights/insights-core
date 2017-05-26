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

from .. import YAMLMapper, mapper, LegacyItemAccess


@mapper('cobbler_settings')
class CobblerSettings(LegacyItemAccess, YAMLMapper):
    """
    Read the ``/etc/cobbler/settings`` YAML file.
    """
    pass
