import doctest
from insights.parsers import avc_hash_stats
from insights.parsers.avc_hash_stats import AvcHashStats
from insights.tests import context_wrap

AVC_HASH_STATS = """
entries: 509
buckets used: 290/512
longest chain: 7
""".strip()


def test_avc_hash_stats():
    hash_stats = avc_hash_stats.AvcHashStats(context_wrap(AVC_HASH_STATS))
    assert hash_stats.entries == 509
    assert hash_stats.buckets == 512
    assert hash_stats.buckets_used == 290
    assert hash_stats.longest_chain == 7


def test_avc_hash_stats_doc_examples():
    env = {
        'avc_hash_stats': AvcHashStats(
            context_wrap(AVC_HASH_STATS)),
    }
    failed, total = doctest.testmod(avc_hash_stats, globs=env)
    assert failed == 0
