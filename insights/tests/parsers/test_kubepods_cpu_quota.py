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
