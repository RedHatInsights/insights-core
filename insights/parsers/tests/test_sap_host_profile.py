#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.parsers import sap_host_profile, SkipException
from insights.parsers.sap_host_profile import SAPHostProfile
from insights.tests import context_wrap
import doctest
import pytest

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
    with pytest.raises(SkipException) as s:
        SAPHostProfile(context_wrap(HOST_PROFILE_AB))
    assert "Incorrect line: 'DIR_GLOBAL'" in str(s)


def test_doc_examples():
    env = {
            'hpf': SAPHostProfile(context_wrap(HOST_PROFILE_DOC)),
          }
    failed, total = doctest.testmod(sap_host_profile, globs=env)
    assert failed == 0
