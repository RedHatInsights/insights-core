from .. import Mapper, mapper, get_active_lines

DRIVER_NAME = 'driver_name'
DEVICE_TYPE = 'device_type'
FIRMWARE_REVISION = 'firmware_revision'


@mapper('hponcfg-g')
class HponConf(Mapper):
    """
    Get the iLO firmware revision from the hponcfg command.
    This is a 3rd party utility from HP and isn't shipped with RHEL.

    Input looks like this::

        HP Lights-Out Online Configuration utility
        Version 4.3.1 Date 05/02/2014 (c) Hewlett-Packard Company, 2014
        Firmware Revision = 1.22 Device type = iLO 4 Driver name = hpilo
        Host Information:
                                Server Name: esxi01.hp.local
                                Server Number:

    Output a dict like this::

        {
            'firmware_revision': '1.22',
            'device_type': 'iLO 4',
            'driver_name': 'hpilo'
            'server_name': esxi01.hp.local
            'server_number': ''
        }
    """

    def parse_content(self, content):
        self.data = {}
        line_iter = iter(get_active_lines(content))
        while True:
            try:

                line = line_iter.next()

                if 'Firmware Revision' in line:
                    line = line.replace('Firmware Revision', '').replace('Device type', '').replace('Driver name', '')
                    val = [x.strip() for x in line.split('=') if x.strip()]
                    self.data[FIRMWARE_REVISION] = val[0]
                    self.data[DEVICE_TYPE] = val[1]
                    self.data[DRIVER_NAME] = val[2]

                if 'Host Information' in line:
                    line = line_iter.next().strip()
                    val = line.split('Server Name:')
                    if len(val) > 1:
                        self.data['server_name'] = val[1].strip()

                    line = line_iter.next().strip()
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
