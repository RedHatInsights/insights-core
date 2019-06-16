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
