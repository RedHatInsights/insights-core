import doctest
import pytest
from insights.parsers import avc_cache_threshold, ParseException
from insights.parsers.avc_cache_threshold import AvcCacheThreshold
from insights.tests import context_wrap

AVC_CACHE_THRESHOLD = """
512
""".strip()

AVC_CACHE_THRESHOLD_INVALID = """
invalid
invalid
invalid
""".strip()


def test_avc_cache_threshold():
    cache_threshold = avc_cache_threshold.AvcCacheThreshold(context_wrap(AVC_CACHE_THRESHOLD))
    assert cache_threshold.cache_threshold == 512


def test_invalid():
    with pytest.raises(ParseException) as e:
        avc_cache_threshold.AvcCacheThreshold(context_wrap(AVC_CACHE_THRESHOLD_INVALID))
    assert "invalid" in str(e)


def test_avc_cache_threshold_doc_examples():
    env = {
        'avc_cache_threshold': AvcCacheThreshold(
            context_wrap(AVC_CACHE_THRESHOLD)),
    }
    failed, total = doctest.testmod(avc_cache_threshold, globs=env)
    assert failed == 0
