import doctest

import pytest
from insights.parsers import ParseException, SkipException
from insights.parsers import sctp
from insights.parsers.sctp import SCTPEps
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


def test_sctp():
    sctp_info = SCTPEps(context_wrap(SCTP_EPS_DETAILS))
    assert sorted(sctp_info.sctp_ports) == sorted(['11165', '11166', '11167', '11168'])
    assert sorted(sctp_info.sctp_local_ips) == sorted(['10.0.0.102', '10.0.0.70', '172.31.1.2', '192.168.11.2'])
    assert sctp_info.sctp_eps_ips == {'ffff88017e0a0200': ['10.0.0.102', '10.0.0.70'],
                                       'ffff880612e81c00': ['10.0.0.102', '10.0.0.70', '172.31.1.2'],
                                       'ffff88061fba9800': ['10.0.0.102', '10.0.0.70'],
                                       'ffff88031e6f1a00': ['10.0.0.102', '10.0.0.70', '192.168.11.2']}
    assert len(sctp_info.search(local_port='11165')) == 1

    with pytest.raises(ParseException) as exc:
        sctp_obj = SCTPEps(context_wrap(SCTP_EPS_DETAILS_NO))
        sctp_obj.sctp_eps_ips
    assert 'Contents are not compatible to this parser' in str(exc)

    with pytest.raises(SkipException) as exc:
        sctp_obj = SCTPEps(context_wrap(SCTP_EPS_DETAILS_NO_2))
        sctp_obj.sctp_eps_ips
    assert 'No Contents' in str(exc)


def test_sctp_doc_examples():
    env = {
        'sctp_info': SCTPEps(context_wrap(SCTP_EPS_DETAILS_DOC)),
    }
    failed, total = doctest.testmod(sctp, globs=env)
    assert failed == 0
