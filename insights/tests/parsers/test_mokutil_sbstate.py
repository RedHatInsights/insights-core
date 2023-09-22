import doctest
import pytest

from insights.parsers import mokutil_sbstate
from insights.parsers.mokutil_sbstate import MokutilSbstate
from insights.tests import context_wrap

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


def test_doc_examples():
    env = {
        "mokutil": MokutilSbstate(context_wrap(SECUREBOOT_ENABLED)),
    }
    failed, total = doctest.testmod(mokutil_sbstate, globs=env)
    assert failed == 0
