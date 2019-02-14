import doctest

import pytest
from insights.parsers import ParseException, SkipException
from insights.parsers import sctp
from insights.parsers.sctp import SCTPEps
from insights.parsers.sctp import SCTPAsc
from insights.tests import context_wrap

SCTP_EPS_DETAILS = """
ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
ffff88017e0a0200 ffff880299f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70
ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 172.31.1.2
ffff88061fba9800 ffff88061f8a3180 2   10  31   11167   200 273361145 10.0.0.102 10.0.0.70
ffff88031e6f1a00 ffff88031dbdb180 2   10  32   11168   200 273365974 10.0.0.102 10.0.0.70 192.168.11.2
""".strip()

SCTP_EPS_DETAILS_NO = """
ENDPT            SOCK             STY SST  LPORT   UID INODE     LADDRS
ffff88017e0a0200 ffff880299f7fa00 2   10   11165   200 299689357 10.0.0.102 10.0.0.70
ffff880612e81c00 ffff8803c28a1b00 2   10   11166   200 273361203 10.0.0.102 10.0.0.70 172.31.1.2
ffff88061fba9800 ffff88061f8a3180 2   10   11167   200 273361145 10.0.0.102 10.0.0.70
ffff88031e6f1a00 ffff88031dbdb180 2   10   11168   200 273365974 10.0.0.102 10.0.0.70 192.168.11.2
""".strip()

SCTP_EPS_DETAILS_DOC = """
ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
ffff88017e0a0200 ffff880299f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70
ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 172.31.1.2
""".strip()

SCTP_EPS_DETAILS_NO_2 = """
""".strip()

SCTP_ASSOC = """
 ASSOC     SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS <-> RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC
ffff88045ac7e000 ffff88062077aa00 2   1   4  1205  963        0        0     200 273361167 11567 11166  10.0.0.102 10.0.0.70 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
ffff88061fbf2000 ffff88060ff92500 2   1   4  1460  942        0        0     200 273360669 11566 11167  10.0.0.102 10.0.0.70 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
ffff8803217b9000 ffff8801c6321580 2   1   4  1675  977        0        0     200 273361369 11565 11168  10.0.0.102 10.0.0.70 192.168.11.2 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
ffff8803db908000 ffff88061e4a00c0 2   1   4  2229  967        0        0     200 273361177 12067 11166  10.0.0.102 10.0.0.70 <-> *10.0.0.110 10.0.0.78      1000     2     2   10    0    0        0
ffff88062258f000 ffff88060fffaa40 2   1   4  2485  953        0        0     200 273360681 12066 11166  10.0.0.102 10.0.0.70 <-> *10.0.0.103 10.0.0.71      1000     2     2   10    0    0        0
ffff8801ce686000 ffff8801c7083ac0 2   1   4  2741  982        0        0     200 273361381 12065 11166  10.0.0.102 10.0.0.70 <-> *10.0.0.112 10.0.0.80      1000     2     2   10    0    0        0
ffff88031e1f4000 ffff8801c6fd9b00 2   1   4  7092 1005        0        0     200 273366011 11567 11167  10.0.0.102 10.0.0.70 <-> *10.0.0.111 10.0.0.79      1000     2     2   10    0    0        0
""".strip()

SCTP_ASSOC_2 = """
 ASSOC     SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS <-> RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC
ffff8804239ca000 ffff8804238c6040 2   1   4  3091    1        0        0     500 90293 37379  3868  10.0.200.114 10.0.201.114 2010:0010:0000:0200:0000:0000:0000:0114 2010:0010:0000:0201:0000:0000:0000:0114 <-> *10.0.100.94 10.0.101.94 2010:0010:0000:0100:0000:0000:0000:0094 2010:0010:0000:0101:0000:0000:0000:0094 	    1000     5     5   10    0    0        0
""".strip()

def test_sctp():
    sctp_info = SCTPEps(context_wrap(SCTP_EPS_DETAILS))
    assert sorted(sctp_info.sctp_local_ports) == sorted(['11165', '11166', '11167', '11168'])
    assert sorted(sctp_info.sctp_local_ips) == sorted(['10.0.0.102', '10.0.0.70', '172.31.1.2', '192.168.11.2'])
    assert sctp_info.sctp_eps_ips == {'ffff88017e0a0200': ['10.0.0.102', '10.0.0.70'],
                                       'ffff880612e81c00': ['10.0.0.102', '10.0.0.70', '172.31.1.2'],
                                       'ffff88061fba9800': ['10.0.0.102', '10.0.0.70'],
                                       'ffff88031e6f1a00': ['10.0.0.102', '10.0.0.70', '192.168.11.2']}
    assert len(sctp_info.search(local_port='11165')) == 1

    sctp_asc = SCTPAsc(context_wrap(SCTP_ASSOC))
    sctp_asc = SCTPAsc(context_wrap(SCTP_ASSOC_2))
    print(sctp_asc.data)
    with pytest.raises(ParseException) as exc:
        sctp_obj = SCTPEps(context_wrap(SCTP_EPS_DETAILS_NO))
        assert sctp_obj is None   # Just added ro remove flake8 warnings
    assert 'Contents are not compatible to this parser' in str(exc)

    with pytest.raises(SkipException) as exc:
        sctp_obj = SCTPEps(context_wrap(SCTP_EPS_DETAILS_NO_2))
        assert sctp_obj is None   # Just added to remove flake8 warnings
    assert 'No Contents' in str(exc)


def test_sctp_doc_examples():
    env = {
        'sctp_info': SCTPEps(context_wrap(SCTP_EPS_DETAILS_DOC)),
        'sctp_asc': SCTPAsc(context_wrap(SCTP_ASSOC)),
    }
    failed, total = doctest.testmod(sctp, globs=env)
    assert failed == 0
