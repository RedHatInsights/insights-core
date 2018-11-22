import doctest
from insights.parsers import avc_cache_threshold
from insights.parsers.avc_cache_threshold import AvcCacheThreshold
from insights.tests import context_wrap

AVC_CACHE_THRESHOLD = """
512
""".strip()


def test_avc_cache_threshold():
    cache_threshold = avc_cache_threshold.AvcCacheThreshold(context_wrap(AVC_CACHE_THRESHOLD))
    assert cache_threshold.value == 512


def test_avc_cache_threshold_doc_examples():
    env = {
        'avc_cache_threshold': AvcCacheThreshold(
            context_wrap(AVC_CACHE_THRESHOLD)),
    }
    failed, total = doctest.testmod(avc_cache_threshold, globs=env)
    assert failed == 0
