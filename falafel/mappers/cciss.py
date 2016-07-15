from falafel.core.plugins import mapper


@mapper('cciss')
def get_cciss(context):
    '''
    Return a dict of cciss info. For example:

    Input:
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

    Output:
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

    cciss_info = dict()
    for line in context.content:
        if line.strip():
            key, val = line.split(":", 1)
            cciss_info[key.strip()] = val.strip()

    return cciss_info
