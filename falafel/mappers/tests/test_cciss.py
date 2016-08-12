from falafel.mappers import cciss
from falafel.tests import context_wrap


CCISS = '''
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
'''


def test_get_cciss():
    cciss_info = cciss.Cciss.parse_context(context_wrap(CCISS))

    assert cciss_info['cciss0'] == 'HP Smart Array P220i Controller'
    assert cciss_info['Board ID'] == "0x3355103c"
    assert cciss_info['Firmware Version'] == '3.42'
    assert cciss_info['IRQ'] == '82'
    assert cciss_info['Logical drives'] == '1'
    assert cciss_info['Sector size'] == '8192'
    assert cciss_info['Current Q depth'] == '0'
    assert cciss_info['Current # commands on controller'] == '0'
    assert cciss_info['Max Q depth since init'] == '84'
    assert cciss_info['Max # commands on controller since init'] == '111'
    assert cciss_info['Max SG entries since init'] == '128'
    assert cciss_info['Sequential access devices'] == '0'
    assert cciss_info['cciss/c0d0'] == '299.96GB   RAID 1(1+0)'
