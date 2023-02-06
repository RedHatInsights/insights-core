import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import blacklisted
from insights.parsers.blacklisted import BlacklistedSpecs
from insights.tests import context_wrap


SPECS = '{"specs": ["insights.specs.default.DefaultSpecs.dmesg", "insights.specs.default.DefaultSpecs.fstab"]}'


def test_blacklisted_doc_examples():
    env = {
        "specs": BlacklistedSpecs(context_wrap(SPECS)),
    }
    failed, total = doctest.testmod(blacklisted, globs=env)
    assert failed == 0


def test_skip():
    with pytest.raises(SkipComponent) as ex:
        BlacklistedSpecs(context_wrap(""))
    assert "Empty output." in str(ex)


def test_blacklist_specs():
    bs = BlacklistedSpecs(context_wrap(SPECS))
    assert bs.specs[0] == "insights.specs.default.DefaultSpecs.dmesg"
