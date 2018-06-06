"""
HponConf - command ``/sbin/hponcfg -g``
=======================================

Get the iLO firmware revision from the ``hponcfg`` command.
This is a 3rd party utility from HP and isn't shipped with RHEL.  However,
it's useful for detecting possible hardware incompatibilities.

There are only five pieces of information extracted:

* **firmware_revision** - the ``Firmware Revision`` value
* **device_type** - the ``Device type`` value
* **driver_name** - the ``Driver name`` value
* **server_name** - the ``Server Name`` value
* **server_number** - the ``Server Number`` value

Values are '' if not listed in the output.

Input looks like this::

    HP Lights-Out Online Configuration utility
    Version 4.3.1 Date 05/02/2014 (c) Hewlett-Packard Company, 2014
    Firmware Revision = 1.22 Device type = iLO 4 Driver name = hpilo
    Host Information:
                            Server Name: esxi01.hp.local
                            Server Number:

Examples:

    >>> cfg = shared[HponConf]
    >>> cfg.data['firmware_revision']
    '1.22'
    >>> cfg.data['server_name']
    'esxi01.hp.local'
    >>> cfg.data['server_number']
    ''
    >>> 'Version' in cfg.data # other values in the hponcfg output not found
    False
"""

from .. import parser, get_active_lines, CommandParser
from insights.specs import Specs

DRIVER_NAME = 'driver_name'
DEVICE_TYPE = 'device_type'
FIRMWARE_REVISION = 'firmware_revision'


@parser(Specs.hponcfg_g)
class HponConf(CommandParser):
    """
    Read the output of the HP ILO configuration utility.

    Attributes:
        firmware_revision (str): The firmware revision string.
        device_type (str): The device type (e.g. 'iLO 4').
        driver_name (str): The driver name (e.g. 'hpilo').
    """

    def parse_content(self, content):
        self.data = {}
        line_iter = iter(get_active_lines(content))
        while True:
            try:

                line = next(line_iter)

                if 'Firmware Revision' in line:
                    line = line.replace('Firmware Revision', '').replace('Device type', '').replace('Driver name', '')
                    val = [x.strip() for x in line.split('=') if x.strip()]
                    self.data[FIRMWARE_REVISION] = val[0]
                    self.data[DEVICE_TYPE] = val[1]
                    self.data[DRIVER_NAME] = val[2]

                if 'Host Information' in line:
                    line = next(line_iter).strip()
                    val = line.split('Server Name:')
                    if len(val) > 1:
                        self.data['server_name'] = val[1].strip()

                    line = next(line_iter).strip()
                    val = line.split('Server Number:')
                    if len(val) > 1:
                        self.data['server_number'] = val[1].strip()

            except StopIteration:
                break

    def __getitem__(self, i):
        return self.data[i]

    @property
    def firmware_revision(self):
        return self.data.get(FIRMWARE_REVISION, None)

    @property
    def device_type(self):
        return self.data.get(DEVICE_TYPE, None)

    @property
    def driver_name(self):
        return self.data.get(DRIVER_NAME, None)
