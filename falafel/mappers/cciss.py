import os
from falafel.core.plugins import mapper
from falafel.core import MapperOutput, computed


@mapper('cciss')
class Cciss(MapperOutput):
    '''
    Raw Data
    -----

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

    Output
    ------

    {
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

    @classmethod
    def parse_context(cls, context):
        cciss_info = {
            "device": os.path.basename(context.path)
        }
        for line in context.content:
            if line.strip():
                key, val = line.split(":", 1)
                cciss_info[key.strip()] = val.strip()

        return cls(cciss_info, context.path)

    @computed
    def firmware_version(self):
        return self.data['Firmware Version']

    @computed
    def model(self):
        return self.data['device']
