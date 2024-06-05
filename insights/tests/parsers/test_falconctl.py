import doctest
import pytest

from insights.core.exceptions import SkipComponent, ParseException
from insights.parsers import falconctl
from insights.parsers.falconctl import FalconctlBackend, FalconctlRfm, FalconctlAid, FalconctlVersion
from insights.tests import context_wrap

BACKEND_1 = """
backend is not set.
""".strip()

BACKEND_2 = """
backend=auto.
""".strip()

BACKEND_INVALID_1 = """
backend?auto.
""".strip()

RFM_1 = """
rfm-state=false.
""".strip()

RFM_2 = """
rfm-state=true.
""".strip()

BACKEND_EMPTY = ""
RFM_EMPTY = ""

AID_VALID = """
aid="44e3b7d20b434a2bb2815d9808fa3a8b".
""".strip()

AID_VALID_UNSET = """
aid is not set.
""".strip()

AID_INVALID_1 = """
aid "44e3b7d20b434a2bb2815d9808fa3a8b" .
""".strip()

AID_INVALID_2 = """
aid"44e3b7d20b434a2bb2815d9808fa3a8b".
""".strip()

AID_INVALID_3 = """
aid="44e3b7d20b434a2bb2815d
9808fa3a8b".
""".strip()

VERSION_VALID = """
version = 7.14.16703.0

""".strip()

VERSION_EMPTY = ""

VERSION_INVALID = """
version 7.14.16703.0

""".strip()


def test_falconctl_1():
    backend_1 = FalconctlBackend(context_wrap(BACKEND_1))
    assert backend_1.backend == "not set"


def test_falconctl_2():
    backend_2 = FalconctlBackend(context_wrap(BACKEND_2))
    assert backend_2.backend == "auto"


def test_rfm():
    rfm = FalconctlRfm(context_wrap(RFM_1))
    assert rfm.rfm is False

    rfm = FalconctlRfm(context_wrap(RFM_2))
    assert rfm.rfm is True


def test_backend_empty():
    with pytest.raises(SkipComponent) as e:
        FalconctlBackend(context_wrap(BACKEND_EMPTY))
    assert 'SkipComponent' in str(e)

    with pytest.raises(ParseException) as e:
        FalconctlBackend(context_wrap(BACKEND_INVALID_1))
    assert 'Invalid content:' in str(e)


def test_rfm_empty():
    with pytest.raises(SkipComponent) as e:
        FalconctlRfm(context_wrap(RFM_EMPTY))
    assert 'SkipComponent' in str(e)


def test_falconctl_aid():
    aid = FalconctlAid(context_wrap(AID_VALID))
    assert aid.aid == "44e3b7d20b434a2bb2815d9808fa3a8b"

    aid = FalconctlAid(context_wrap(AID_VALID_UNSET))
    assert aid.aid == "not set"


def test_falconctl_aid_invalid():
    with pytest.raises(SkipComponent) as e:
        FalconctlAid(context_wrap(""))
    assert 'Empty.' in str(e)

    with pytest.raises(ParseException) as e:
        FalconctlAid(context_wrap(AID_INVALID_1))
    assert 'Invalid content:' in str(e)

    with pytest.raises(ParseException) as e:
        FalconctlAid(context_wrap(AID_INVALID_2))
    assert 'Invalid content:' in str(e)

    with pytest.raises(ParseException) as e:
        FalconctlAid(context_wrap(AID_INVALID_2))
    assert 'Invalid content:' in str(e)


def test_falconctl_version():
    falcon_version = FalconctlVersion(context_wrap(VERSION_VALID))
    assert falcon_version.version == "7.14.16703.0"


def test_falconctl_version_invalid():
    with pytest.raises(SkipComponent) as e:
        FalconctlVersion(context_wrap(VERSION_EMPTY))
    assert 'Empty.' in str(e)

    with pytest.raises(ParseException) as e:
        FalconctlVersion(context_wrap(VERSION_INVALID))
    assert 'Invalid content:' in str(e)


def test_falcontcl_doc_examples():
    env = {
        "falconctlbackend": FalconctlBackend(context_wrap(BACKEND_2)),
        "falconctlrfm": FalconctlRfm(context_wrap(RFM_1)),
        "falconctlaid": FalconctlAid(context_wrap(AID_VALID)),
        "falconctlversion": FalconctlVersion(context_wrap(VERSION_VALID))
    }
    failed, total = doctest.testmod(falconctl, globs=env)
    assert failed == 0
