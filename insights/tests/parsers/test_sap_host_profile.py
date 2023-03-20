import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import sap_host_profile
from insights.parsers.sap_host_profile import SAPHostProfile
from insights.tests import context_wrap

HOST_PROFILE_DOC = """
SAPSYSTEMNAME = SAP
SAPSYSTEM = 99
service/porttypes = SAPHostControl SAPOscol SAPCCMS
DIR_LIBRARY =
DIR_EXECUTABLE = /usr/sap/hostctrl/exe
DIR_PROFILE = /usr/sap/hostctrl/exe
DIR_GLOBAL = /usr/sap/hostctrl/exe
DIR_INSTANCE = /usr/sap/hostctrl/exe
DIR_HOME = /usr/sap/hostctrl/work
""".strip()

HOST_PROFILE_AB = """
SAPSYSTEMNAME = SAP
SAPSYSTEM = 99
service/porttypes = SAPHostControl SAPOscol SAPCCMS
DIR_LIBRARY = /usr/sap/hostctrl/exe
DIR_EXECUTABLE = /usr/sap/hostctrl/exe
DIR_PROFILE = /usr/sap/hostctrl/exe
DIR_GLOBAL
""".strip()


def test_sap_host_profile():
    hpf = SAPHostProfile(context_wrap(HOST_PROFILE_DOC))
    assert "SAPSYSTEM" in hpf
    assert hpf["DIR_GLOBAL"] == "/usr/sap/hostctrl/exe"
    assert hpf["DIR_LIBRARY"] == ""


def test_sap_host_profile_abnormal():
    with pytest.raises(SkipComponent) as s:
        SAPHostProfile(context_wrap(HOST_PROFILE_AB))
    assert "Incorrect line: 'DIR_GLOBAL'" in str(s)


def test_doc_examples():
    env = {
            'hpf': SAPHostProfile(context_wrap(HOST_PROFILE_DOC)),
          }
    failed, total = doctest.testmod(sap_host_profile, globs=env)
    assert failed == 0
