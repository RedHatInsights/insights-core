import doctest
import pytest
from insights.parsers import od_cpu_dma_latency
from insights.parsers.od_cpu_dma_latency import OdCpuDmaLatency
from insights.tests import context_wrap
from insights.parsers import SkipException


CONTENT_OD_CPU_DMA_LATENCY = """
  2000000000
"""

CONTENT_OD_CPU_DMA_LATENCY_EMPTY = ""


def test_doc_examples():
    env = {'cpu_dma_latency': OdCpuDmaLatency(context_wrap(CONTENT_OD_CPU_DMA_LATENCY))}
    failed, total = doctest.testmod(od_cpu_dma_latency, globs=env)
    assert failed == 0


def test_OdCpuDmaLatency():
    d = OdCpuDmaLatency(context_wrap(CONTENT_OD_CPU_DMA_LATENCY))
    assert d.force_latency == 2000000000

    with pytest.raises(SkipException):
        OdCpuDmaLatency(context_wrap(CONTENT_OD_CPU_DMA_LATENCY_EMPTY))
