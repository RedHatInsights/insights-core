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
