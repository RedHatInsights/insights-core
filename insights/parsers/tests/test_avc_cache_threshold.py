#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
