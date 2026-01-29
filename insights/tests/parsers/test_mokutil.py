import doctest
import pytest

from insights.parsers import mokutil
from insights.parsers.mokutil import MokutilDbShort, MokutilSbstate
from insights import SkipComponent
from insights.tests import context_wrap

MOKUTIL_DB_SHORT_OUTPUT = """
b7b180e323 Signature Database key
46def63b5c Microsoft Corporation UEFI CA 2011
""".strip()

MOKUTIL_DB_BAD_FORMAT = """
b7b180e323
46def63b5c Microsoft Corporation UEFI CA 2011
""".strip()

MOKUTIL_DB_EMPTY = """
""".strip()

SECUREBOOT_ENABLED = """
SecureBoot enabled
""".strip()

SECUREBOOT_DISABLED = """
SecureBoot disabled
""".strip()

NOT_SUPPORTED = """
EFI variables are not supported on this system
""".strip()

TEST_CASES = [
    (SECUREBOOT_ENABLED, True),
    (SECUREBOOT_DISABLED, False),
    (NOT_SUPPORTED, None)
]


@pytest.mark.parametrize("output, boolean", TEST_CASES)
def test_mokutil(output, boolean):
    test = MokutilSbstate(context_wrap(output))
    assert test.secureboot_enabled == boolean


def test_mokutil_db_short():
    mokutil = MokutilDbShort(context_wrap(MOKUTIL_DB_SHORT_OUTPUT))
    assert len(mokutil) == 2
    assert sorted(mokutil.keys()) == ['46def63b5c', 'b7b180e323']
    assert mokutil['b7b180e323'] == 'Signature Database key'
    assert mokutil['46def63b5c'] == 'Microsoft Corporation UEFI CA 2011'

    with pytest.raises(SkipComponent):
        MokutilDbShort(context_wrap(MOKUTIL_DB_BAD_FORMAT))
    with pytest.raises(SkipComponent):
        MokutilDbShort(context_wrap(MOKUTIL_DB_EMPTY))


def test_doc_examples():
    env = {
        "mokutil_db_short": MokutilDbShort(context_wrap(MOKUTIL_DB_SHORT_OUTPUT)),
        "mokutil": MokutilSbstate(context_wrap(SECUREBOOT_ENABLED)),
    }
    failed, _ = doctest.testmod(mokutil, globs=env)
    assert failed == 0
