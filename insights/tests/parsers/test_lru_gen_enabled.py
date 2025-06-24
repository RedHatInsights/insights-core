import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import lru_gen_enabled
from insights.parsers.lru_gen_enabled import LruGenEnabled
from insights.tests import context_wrap

LRU_GEN_DISABLED = "0x0000"
LRU_GEN_ENABLED = "0x0004"


def test_lru_gen_enabled():
    lru_gen_enabled = LruGenEnabled(context_wrap(LRU_GEN_DISABLED))
    assert lru_gen_enabled.enabled is False
    assert lru_gen_enabled.features == 0

    lru_gen_enabled = LruGenEnabled(context_wrap(LRU_GEN_ENABLED))
    assert lru_gen_enabled.enabled is True
    assert lru_gen_enabled.features == 4


LRU_GEN_MULTIPLE_LINES = """
line 1
line 2
""".strip()


def test_lru_gen_exceptions():
    with pytest.raises(SkipComponent) as err:
        LruGenEnabled(context_wrap(LRU_GEN_MULTIPLE_LINES))
    assert "Input content should only contain one line" in str(err)

    with pytest.raises(SkipComponent) as err:
        LruGenEnabled(context_wrap(""))
    assert "Input content should only contain one line" in str(err)

    with pytest.raises(ParseException) as err:
        LruGenEnabled(context_wrap("1"))
    assert "Input content is not a hex number" in str(err)

    with pytest.raises(ParseException) as err:
        LruGenEnabled(context_wrap("0xtest"))
    assert "Input content is not a hex number" in str(err)


def test_lru_gen_enabled_doc_examples():
    env = {
        'lru_gen_enabled': LruGenEnabled(context_wrap(LRU_GEN_ENABLED)),
    }
    failed, total = doctest.testmod(lru_gen_enabled, globs=env)
    assert failed == 0
