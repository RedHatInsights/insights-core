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

from insights.parsers.ovirt_engine_confd import OvirtEngineConfd
from insights.tests import context_wrap


CONFD_MATCH = """
JBOSS_HOME="/usr/share/jbossas"
ENGINE_PKI="/etc/pki/ovirt-engine"
ENGINE_PKI_CA="/etc/pki/ovirt-engine/ca.pem"
ENGINE_PKI_ENGINE_CERT="/etc/pki/ovirt-engine/certs/engine.cer"
ENGINE_TMP="${ENGINE_VAR}/tmp"
""".strip()

CONFD_NOT_MATCH = """
JBOSS_HOME="/usr/share/jbossas"
ENGINE_PKI="/etc/pki/ovirt-engine"
ENGINE_PKI_CA="/etc/pki/ovirt-engine/ca.pem"
ENGINE_PKI_ENGINE_CERT="/etc/pki/ovirt-engine/certs/engine.cer"
""".strip()


def test_ovirt_engine_confd():
    match_result = OvirtEngineConfd(context_wrap(CONFD_MATCH))
    assert 'tmp' in match_result.get('ENGINE_TMP')
    no_match_result = OvirtEngineConfd(context_wrap(CONFD_NOT_MATCH))
    assert no_match_result.get('ENGINE_TMP') is None
