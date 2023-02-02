import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import nfnetlink_queue
from insights.tests import context_wrap
from insights.tests.parsers import skip_component_check


NFNETLINK_QUEUE = """
    0  -4423     0 2 65535     0     0       22  1
    1  -4424     0 2 65535     0     0       27  1
    2  -4425     0 2 65535     0     0       17  1
    3  -4426     0 2 65535     0     0       14  1
    4  -4427     0 2 65535     0     0       22  1
    5  -4428     0 2 65535     0     0       16  1
""".strip()

CORRUPT_NFNETLINK_QUEUE_1 = """
    0  -4423     0 2 65535     0     0       22  1
    1  -4424     0 2 6553
    2  -4425     0 2 65535     0     0       17  1
    3  -4426     0 2 65535     0     0       14  1
    4  -4427     0 2 65535     0     0       22  1
    5  -4428     0 2 65535     0     0       16  1
""".strip()

CORRUPT_NFNETLINK_QUEUE_2 = """
    0  -4423     0 2 65535     0     0       22  1
    1  -4424     0 2 astring   0     0       27  1
    2  -4425     0 2 65535     0     0       17  1
    3  -4426     0 2 65535     0     0       14  1
    4  -4427     0 2 65535     0     0       22  1
    5  -4428     0 2 65535     0     0       16  1
""".strip()

NFNETLINK_DOC = """
0  -4423     0 2 65535     0     0       22  1
1  -4424     0 2 65535     0     0       27  1
""".strip()


def test_nfnetlink_doc_examples():
    env = {
        'nf': nfnetlink_queue.NfnetLinkQueue(context_wrap(NFNETLINK_DOC))
    }
    failed, total = doctest.testmod(nfnetlink_queue, globs=env)
    assert failed == 0


def test_parse_content():
    nfnet_link_queue = nfnetlink_queue.NfnetLinkQueue(context_wrap(NFNETLINK_QUEUE))
    row = nfnet_link_queue.data[0]
    assert row["queue_number"] == 0
    assert row["peer_portid"] == -4423
    assert row["queue_total"] == 0
    assert row["copy_mode"] == 2
    assert row["copy_range"] == 65535
    assert row["queue_dropped"] == 0
    assert row["user_dropped"] == 0
    assert row["id_sequence"] == 22

    row = nfnet_link_queue.data[5]
    assert row["queue_number"] == 5
    assert row["peer_portid"] == -4428
    assert row["queue_total"] == 0
    assert row["copy_mode"] == 2
    assert row["copy_range"] == 65535
    assert row["queue_dropped"] == 0
    assert row["user_dropped"] == 0
    assert row["id_sequence"] == 16


def test_missing_columns():
    with pytest.raises(ParseException):
        nfnetlink_queue.NfnetLinkQueue(context_wrap(CORRUPT_NFNETLINK_QUEUE_1))


def test_wrong_type():
    with pytest.raises(ValueError):
        nfnetlink_queue.NfnetLinkQueue(context_wrap(CORRUPT_NFNETLINK_QUEUE_2))


def test_empty_content():
    skip_component_check(nfnetlink_queue.NfnetLinkQueue)
