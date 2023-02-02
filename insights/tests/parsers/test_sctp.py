import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import sctp
from insights.parsers.sctp import SCTPAsc, SCTPAsc7, SCTPEps, SCTPSnmp
from insights.tests import context_wrap

SCTP_EPS_DETAILS = """
ENDPT            SOCK             STY SST HBKT LPORT   UID INODE     LADDRS
ffff88017e0a0200 ffff880299f7fa00 2   10  29   11165   200 299689357 10.0.0.102 10.0.0.70
ffff880612e81c00 ffff8803c28a1b00 2   10  30   11166   200 273361203 10.0.0.102 10.0.0.70 172.31.1.2
ffff88061fba9800 ffff88061f8a3180 2   10  31   11167   200 273361145 10.0.0.102 10.0.0.70
ffff88031e6f1a00 ffff88031dbdb180 2   10  32   11168   200 273365974 10.0.0.102 10.0.0.70 192.168.11.2
ffff88031e6f1a00 ffff88031dbdb180 2   10  32   11168   200 273365974 192.168.11.12
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

SCTP_ASSOC_DOC = """
 ASSOC     SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS <-> RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC
ffff88045ac7e000 ffff88062077aa00 2   1   4  1205  963        0        0     200 273361167 11567 11166  10.0.0.102 10.0.0.70 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
ffff88061fbf2000 ffff88060ff92500 2   1   4  1460  942        0        0     200 273360669 11566 11167  10.0.0.102 10.0.0.70 <-> *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
""".strip()

SCTP_ASSOC_NO = """
""".strip()

SCTP_ASSOC_NO_2 = """
SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC
ffff88045ac7e000 ffff88062077aa00 2   1   4  1205  963        0        0     200 273361167 11567 11166  10.0.0.102 10.0.0.70 *10.0.0.109 10.0.0.77      1000     2     2   10    0    0        0
""".strip()

SCTP_SNMP = """
SctpCurrEstab                   	5380
SctpActiveEstabs                	12749
SctpPassiveEstabs               	55
SctpAborteds                    	2142
SctpShutdowns                   	5295
SctpOutOfBlues                  	36786
SctpChecksumErrors              	0
SctpOutCtrlChunks               	1051492
SctpOutOrderChunks              	17109
SctpOutUnorderChunks            	0
SctpInCtrlChunks                	1018398
SctpInOrderChunks               	17033
SctpInUnorderChunks             	0
SctpFragUsrMsgs                 	0
SctpReasmUsrMsgs                	0
SctpOutSCTPPacks                	1068678
""".strip()

SCTP_SNMP_NO_1 = """
""".strip()

SCTP_SNMP_NO_2 = """
SctpCurrEstab 5380 SctpActiveEstabs 12749 SctpPassiveEstabs 55 SctpAborteds 2142 SctpShutdowns 5295 SctpOutOfBlues 36786 SctpChecksumErrors 0 SctpOutCtrlChunks 1051492 SctpOutOrderChunks 17109
""".strip()

SCTP_SNMP_DOC = """
SctpCurrEstab                   	5380
SctpActiveEstabs                	12749
SctpPassiveEstabs               	55
SctpAborteds                    	2142
SctpShutdowns                   	5295
SctpOutOfBlues                  	36786
SctpChecksumErrors              	0
SctpOutCtrlChunks               	1051492
"""

SCTP_ASC_7 = """
 ASSOC     SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS <-> RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC wmema wmemq sndbuf rcvbuf
ffff8805d36b3000 ffff880f8911f380 0   10  3  0    12754        0        0       0 496595 3868   3868  10.131.222.5 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        11        12  1000000  2000000
ffff8805f17e1000 ffff881004aff380 0   10  3  0    12728        0        0       0 532396 3868   3868  10.131.222.3 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        13        14  3000000  4000000
ffff8805f17e0000 ffff880f8a117380 0   10  3  0    12727        0        0       0 582963 3868   3868  10.131.222.8 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        15        16  5000000  6000000
ffff88081d0bc000 ffff880f6fa66300 0   10  3  0    12726        0        0       0 582588 3868   3868  10.131.222.2 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        17        18  7000000  8000000
ffff88081d0f5000 ffff880f00a99600 0   10  3  0    12725        0        0       0 578082 3868   3868  10.131.222.1 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        19        20  9000000  10000000
""".strip()

SCTP_ASSOC_RHEL_7_DOC = """
 ASSOC     SOCK   STY SST ST HBKT ASSOC-ID TX_QUEUE RX_QUEUE UID INODE LPORT RPORT LADDRS <-> RADDRS HBINT INS OUTS MAXRT T1X T2X RTXC wmema wmemq sndbuf rcvbuf
ffff8805d36b3000 ffff880f8911f380 0   10  3  0    12754        0        0       0 496595 3868   3868  10.131.222.5 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        11        12  1000000  2000000
ffff8805f17e1000 ffff881004aff380 0   10  3  0    12728        0        0       0 532396 3868   3868  10.131.222.3 <-> *10.131.160.81 10.131.176.81        30000    17    10   10    0    0        0        13        14  3000000  4000000
""".strip()


def test_sctp_eps():
    sctp_info = SCTPEps(context_wrap(SCTP_EPS_DETAILS))
    assert sorted(sctp_info.sctp_local_ports) == sorted(['11165', '11166', '11167', '11168'])
    assert sorted(sctp_info.sctp_local_ips) == sorted(['10.0.0.102', '10.0.0.70', '172.31.1.2', '192.168.11.2', '192.168.11.12'])
    assert sctp_info.sctp_eps_ips == {'ffff88017e0a0200': ['10.0.0.102', '10.0.0.70'],
                                       'ffff880612e81c00': ['10.0.0.102', '10.0.0.70', '172.31.1.2'],
                                       'ffff88061fba9800': ['10.0.0.102', '10.0.0.70'],
                                       'ffff88031e6f1a00': ['10.0.0.102', '10.0.0.70', '192.168.11.2', '192.168.11.12']}
    assert len(sctp_info.search(local_port='11165')) == 1


def test_sctp_asc():
    sctp_asc = SCTPAsc(context_wrap(SCTP_ASSOC))
    assert sorted(sctp_asc.sctp_local_ports) == sorted(['11567', '11566', '11565', '12067', '12065', '12066'])
    assert sorted(sctp_asc.search(local_port='11565')) == sorted([{'init_chunks_send': '0', 'uid': '200', 'shutdown_chunks_send': '0', 'max_outstream': '2', 'tx_que': '0', 'inode': '273361369', 'hrtbt_intrvl': '1000', 'sk_type': '2', 'remote_addr': ['*10.0.0.109', '10.0.0.77'], 'data_chunks_retrans': '0', 'local_addr': ['10.0.0.102', '10.0.0.70', '192.168.11.2'], 'asc_id': '977', 'max_instream': '2', 'remote_port': '11168', 'asc_state': '4', 'max_retrans_atmpt': '10', 'sk_state': '1', 'socket': 'ffff8801c6321580', 'asc_struct': 'ffff8803217b9000', 'local_port': '11565', 'hash_bkt': '1675', 'rx_que': '0'}])
    assert len(sctp_asc.search(local_port='11567')) == 2
    assert sorted(sctp_asc.sctp_local_ips) == sorted(['10.0.0.102', '10.0.0.70', '192.168.11.2'])
    assert sorted(sctp_asc.sctp_remote_ips) == sorted(['*10.0.0.109', '10.0.0.77', '*10.0.0.110', '10.0.0.78', '*10.0.0.103', '10.0.0.71', '*10.0.0.112', '10.0.0.80', '*10.0.0.111', '10.0.0.79'])

    sctp_asc = SCTPAsc(context_wrap(SCTP_ASSOC_2))
    assert sorted(sctp_asc.sctp_local_ips) == sorted(['10.0.200.114', '10.0.201.114', '2010:0010:0000:0200:0000:0000:0000:0114', '2010:0010:0000:0201:0000:0000:0000:0114'])
    assert sorted(sctp_asc.sctp_remote_ips) == sorted(['*10.0.100.94', '10.0.101.94', '2010:0010:0000:0100:0000:0000:0000:0094', '2010:0010:0000:0101:0000:0000:0000:0094'])

    sctp_asc = SCTPAsc7(context_wrap(SCTP_ASC_7))
    assert sctp_asc.sctp_local_ips == sorted(['10.131.222.5', '10.131.222.3', '10.131.222.8', '10.131.222.2', '10.131.222.1'])
    assert sctp_asc.data[0]['rcvbuf'] == '2000000'
    assert sctp_asc.data[1]['wmemq'] == '14'
    assert sctp_asc.data[1]['rcvbuf'] == '4000000'


def test_sctp_eps_exceptions():
    with pytest.raises(ParseException) as exc:
        sctp_obj = SCTPEps(context_wrap(SCTP_EPS_DETAILS_NO))
        assert sctp_obj is None   # Just added to remove flake8 warnings
    assert 'The following line is not compatible with this parser' in str(exc)

    with pytest.raises(SkipComponent) as exc:
        sctp_obj = SCTPEps(context_wrap(SCTP_EPS_DETAILS_NO_2))
        assert sctp_obj is None   # Just added to remove flake8 warnings
    assert 'No Contents' in str(exc)


def test_sctp_asc_exceptions():
    with pytest.raises(ParseException) as exc:
        sctp_asc = SCTPAsc(context_wrap(SCTP_ASSOC_NO_2))
        assert sctp_asc is None
    assert 'The following line is not compatible with this parser' in str(exc)
    with pytest.raises(SkipComponent) as exc:
        sctp_asc = SCTPAsc(context_wrap(SCTP_ASSOC_NO))
        assert sctp_asc is None
    assert 'No Contents' in str(exc)


def test_sctp_doc_examples():
    env = {
        'sctp_info': SCTPEps(context_wrap(SCTP_EPS_DETAILS_DOC)),
        'sctp_asc': SCTPAsc(context_wrap(SCTP_ASSOC_DOC)),
        'sctp_asc_7': SCTPAsc7(context_wrap(SCTP_ASSOC_RHEL_7_DOC)),
        'sctp_snmp': SCTPSnmp(context_wrap(SCTP_SNMP_DOC))
    }
    failed, total = doctest.testmod(sctp, globs=env)
    assert failed == 0


def test_sctp_snmp():
    sctp_snmp = SCTPSnmp(context_wrap(SCTP_SNMP))
    assert sorted(sctp_snmp) == sorted({'SctpCurrEstab': 5380, 'SctpActiveEstabs': 12749, 'SctpPassiveEstabs': 55, 'SctpAborteds': 2142, 'SctpShutdowns': 5295, 'SctpOutOfBlues': 36786, 'SctpChecksumErrors': 0, 'SctpOutCtrlChunks': 1051492, 'SctpOutOrderChunks': 17109, 'SctpOutUnorderChunks': 0, 'SctpInCtrlChunks': 1018398, 'SctpInOrderChunks': 17033, 'SctpInUnorderChunks': 0, 'SctpFragUsrMsgs': 0, 'SctpReasmUsrMsgs': 0, 'SctpOutSCTPPacks': 1068678})

    assert sctp_snmp.get('SctpCurrEstab') == 5380
    assert sctp_snmp.get('SctpReasmUsrMsgs') == 0

    assert sctp_snmp.get('something_else') is None


def test_sctp_snmp_exceptions():
    with pytest.raises(SkipComponent) as exc:
        sctp_snmp = SCTPSnmp(context_wrap(SCTP_SNMP_NO_1))
        assert sctp_snmp is None

    assert 'No Contents' in str(exc)

    with pytest.raises(ParseException) as exc:
        sctp_snmp = SCTPSnmp(context_wrap(SCTP_SNMP_NO_2))
        assert sctp_snmp is None

    assert 'Contents are not compatible to this parser' in str(exc)
