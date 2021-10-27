from insights.core.filters import add_filter
from insights.specs import Specs
from insights.tests import context_wrap, DEFAULT_RELEASE, DEFAULT_HOSTNAME

DATA = """
One
Two
Three
Four
"""
DATA_FILTERED = """
Two
Four
"""

add_filter(Specs.messages, ["Two", "Four", "Five"])


def test_context_wrap_unfiltered():
    context = context_wrap(DATA)
    assert context is not None
    assert context.content == DATA.strip().splitlines()
    assert context.release == DEFAULT_RELEASE
    assert context.hostname == DEFAULT_HOSTNAME
    assert context.version == ["-1", "-1"]
    assert context.machine_id == "machine_id"


def test_context_wrap_filtered():
    context = context_wrap(DATA, filtered_spec=Specs.messages)
    assert context is not None
    assert context.content == DATA_FILTERED.strip().splitlines()
