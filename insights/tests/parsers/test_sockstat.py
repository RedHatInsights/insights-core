import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import sockstat
from insights.parsers.sockstat import SockStats
from insights.tests import context_wrap


SOCK_STATS = """
sockets: used 3037
TCP: inuse 1365 orphan 17 tw 2030 alloc 2788 mem 4109
UDP: inuse 6 mem 3
UDPLITE: inuse 0
RAW: inuse 0
FRAG: inuse 0 memory 10
""".strip()

SOCK_STATS_NO = """
""".strip()

SOCK_STATS_DOC = """
sockets: used 3037
TCP: inuse 1365 orphan 17 tw 2030 alloc 2788 mem 4109
UDP: inuse 6 mem 3
UDPLITE: inuse 0
RAW: inuse 0
FRAG: inuse 0 memory 0
""".strip()

SOCK_STATS_NO_2 = """
In valid data is present
""".strip()


def test_sockstat():
    stats = SockStats(context_wrap(SOCK_STATS))
    assert stats.seg_details('sockets') == {'used': '3037'}
    assert stats.seg_details('tcp') == {'inuse': '1365', 'orphan': '17', 'tw': '2030', 'alloc': '2788', 'mem': '4109'}
    assert stats.seg_element_details('tcp', 'inuse') == 1365
    assert stats.seg_element_details('frag', 'memory') == 10
    assert stats.seg_element_details('xyz', 'abc') is None
    assert stats.seg_element_details(None, None) is None
    assert stats.seg_element_details('tcp', 'abc') is None
    assert len(stats.sock_stats)
    with pytest.raises(SkipComponent) as exc:
        sock_obj = SockStats(context_wrap(SOCK_STATS_NO))
        assert sock_obj is not None
    assert 'No Contents' in str(exc)


def test_modinfo_doc_examples():
    env = {'sock_obj': SockStats(context_wrap(SOCK_STATS_DOC))}
    failed, total = doctest.testmod(sockstat, globs=env)
    assert failed == 0
