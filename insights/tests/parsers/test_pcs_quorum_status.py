import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import pcs_quorum_status
from insights.parsers.pcs_quorum_status import PcsQuorumStatus
from insights.tests import context_wrap

PCS_QUORUM_STATUS = """
Quorum information
------------------
Date:             Wed Jun 29 13:17:02 2016
Quorum provider:  corosync_votequorum
Nodes:            2
Node ID:          1
Ring ID:          1/8272
Quorate:          Yes

Votequorum information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      3
Quorum:           2
Flags:            Quorate Qdevice

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
         1          1    A,V,NMW node1 (local)
         2          1    A,V,NMW node2
         0          1            Qdevice
""".strip()

PCS_QUORUM_STATUS_INVALID = """
Quorum information
------------------
Date:             Wed Jun 29 13:17:02 2016
Quorum provider:  corosync_votequorum
Nodes:            2
Node ID:          1
Ring ID:          1/8272
Quorate:          Yes

XXXX invalid information
----------------------
Expected votes:   3
Highest expected: 3
Total votes:      3
Quorum:           2
Flags:            Quorate Qdevice

Membership information
----------------------
    Nodeid      Votes    Qdevice Name
         1          1    A,V,NMW node1 (local)
         2          1    A,V,NMW node2
         0          1            Qdevice
""".strip()

PCS_QUORUM_STATUS_EMPTY = """
""".strip()


def test_pcs_quorum_status():
    pcs_quorum_status = PcsQuorumStatus(context_wrap(PCS_QUORUM_STATUS))
    assert pcs_quorum_status.quorum_info['Date'] == 'Wed Jun 29 13:17:02 2016'
    assert pcs_quorum_status.votequorum_info['Highest expected'] == '3'
    assert pcs_quorum_status.membership_info[2]['Qdevice'] == ''
    assert len(pcs_quorum_status.membership_info) == 3
    assert pcs_quorum_status.membership_info[1] == {'Nodeid': '2', 'Votes': '1', 'Qdevice': 'A,V,NMW',
                                                    'Name': 'node2'}


def test_invalid():
    with pytest.raises(ParseException) as e:
        PcsQuorumStatus(context_wrap(PCS_QUORUM_STATUS_INVALID))
    assert "Incorrect content" in str(e)


def test_empty():
    with pytest.raises(SkipComponent) as e:
        PcsQuorumStatus(context_wrap(PCS_QUORUM_STATUS_EMPTY))
    assert "Empty content" in str(e)


def test_pcs_quorum_status_doc_examples():
    env = {
        'pcs_quorum_status': PcsQuorumStatus(
            context_wrap(PCS_QUORUM_STATUS)),
    }
    failed, total = doctest.testmod(pcs_quorum_status, globs=env)
    assert failed == 0
