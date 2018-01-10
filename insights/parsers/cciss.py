"""
Cciss - Files ``/proc/driver/cciss/cciss*``
===========================================

Reads the ``/proc/driver/cciss/cciss*`` files and converts them into a
dictionary in the *data* property.

Example:
    >>> cciss = shared[Cciss]
    >>> cciss.data['Logical drives']
    '1'
    >>> 'IRQ' in cciss.data
    True
    >>> cciss.model
    'HP Smart Array P220i Controller'
    >>> cciss.firmware_version
    '3.42'
"""

from .. import Parser, parser
from insights.specs import Specs


@parser(Specs.cciss)
class Cciss(Parser):
    '''
    Class for parsing the content of ``/etc/device/cciss*``

    Raw Data::

        cciss0: HP Smart Array P220i Controller
        Board ID: 0x3355103c
        Firmware Version: 3.42
        IRQ: 82
        Logical drives: 1
        Sector size: 8192
        Current Q depth: 0
        Current # commands on controller: 0
        Max Q depth since init: 84
        Max # commands on controller since init: 111
        Max SG entries since init: 128
        Sequential access devices: 0

        cciss/c0d0:  299.96GB   RAID 1(1+0)

    Output::

        data = {
            "Sequential access devices": "0",
            "Current Q depth": "0",
            "cciss0": "HP Smart Array P220i Controller",
            "Board ID": "0x3355103c",
            "IRQ": "82",
            "cciss/c0d0": "299.96GB   RAID 1(1+0)",
            "Logical drives": "1",
            "Current # commands on controller": "0",
            "Sector size": "8192",
            "Firmware Version": "3.42",
            "Max # commands on controller since init": "111",
            "Max SG entries since init": "128",
            "Max Q depth since init": "84"
        }

    '''

    def parse_content(self, content):
        self.device = self.file_name
        self.data = {}

        for line in content:
            if line.strip():
                key, val = line.split(":", 1)
                self.data[key.strip()] = val.strip()

    @property
    def firmware_version(self):
        '''Return the Firmware Version.'''
        return self.data.get('Firmware Version')

    @property
    def model(self):
        '''Return the full model name of the cciss device.'''
        return self.data.get(self.device)
