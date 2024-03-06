import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import falcontcl
from insights.parsers.falcontcl import FalconctlBackend, FalconctlRfm
from insights.tests import context_wrap

BACKEND_1 = """
backend is not set.
""".strip()

BACKEND_2 = """
backend=auto.
""".strip()

RFM = """
rfm-state=false.
""".strip()

BACKEND_EMPTY = ""
RFM_EMPTY = ""


def test_falcontcl_1():
    backend_1 = FalconctlBackend(context_wrap(BACKEND_1))
    assert backend_1.backend == "not set"


def test_falcontcl_2():
    backend_2 = FalconctlBackend(context_wrap(BACKEND_2))
    assert backend_2.backend == "auto"


def test_rfm():
    rfm = FalconctlRfm(context_wrap(RFM))
    assert rfm.rfm is False


def test_backend_empty():
    with pytest.raises(SkipComponent) as e:
        FalconctlBackend(context_wrap(BACKEND_EMPTY))
    assert 'SkipComponent' in str(e)


def test_rfm_empty():
    with pytest.raises(SkipComponent) as e:
        FalconctlRfm(context_wrap(RFM_EMPTY))
    assert 'SkipComponent' in str(e)


def test_falcontcl_doc_examples():
    env = {
        "falconctlbackend": FalconctlBackend(context_wrap(BACKEND_2)),
        "falconctlrfm": FalconctlRfm(context_wrap(RFM))
    }
    failed, total = doctest.testmod(falcontcl, globs=env)
    assert failed == 0
