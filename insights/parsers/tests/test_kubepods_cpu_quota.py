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
from insights.parsers import kubepods_cpu_quota, ParseException
from insights.parsers.kubepods_cpu_quota import KubepodsCpuQuota
from insights.tests import context_wrap

KUBEPODS_CPU_QUOTA_1 = """
-1
""".strip()

KUBEPODS_CPU_QUOTA_2 = """
50000
""".strip()

KUBEPODS_CPU_QUOTA_INVALID = """
invalid
-1
""".strip()


def test_kubepods_cpu_quota():
    cpu_quota = kubepods_cpu_quota.KubepodsCpuQuota(context_wrap(KUBEPODS_CPU_QUOTA_1))
    assert cpu_quota.cpu_quota == -1


def test_kubepods_cpu_quota_2():
    cpu_quota = kubepods_cpu_quota.KubepodsCpuQuota(context_wrap(KUBEPODS_CPU_QUOTA_2))
    assert cpu_quota.cpu_quota == 50000


def test_invalid():
    with pytest.raises(ParseException) as e:
        kubepods_cpu_quota.KubepodsCpuQuota(context_wrap(KUBEPODS_CPU_QUOTA_INVALID))
    assert "invalid" in str(e)


def test_akubepods_cpu_quota_doc_examples():
    env = {
        'kubepods_cpu_quota': KubepodsCpuQuota(
            context_wrap(KUBEPODS_CPU_QUOTA_1)),
    }
    failed, total = doctest.testmod(kubepods_cpu_quota, globs=env)
    assert failed == 0
