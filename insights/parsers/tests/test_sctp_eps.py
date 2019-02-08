import doctest
import pytest
from insights.parsers import modinfo, ParseException, SkipException
from insights.parsers.sctp_eps import SCTPEps
from insights.tests import context_wrap

SCTP_EPS_DETAILS = """
ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
ffff88017e0a0200 ffff880299f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70 
ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 
ffff88061fba9800 ffff88061f8a3180 2   10  31   11167   200 273361145 10.0.0.102 10.0.0.70 
ffff88031e6f1a00 ffff88031dbdb180 2   10  32   11168   200 273365974 10.0.0.102 10.0.0.70
""".strip()

def test_sctp_eps():
    sctp_info = SCTPEps(context_wrap(SCTP_EPS_DETAILS))
