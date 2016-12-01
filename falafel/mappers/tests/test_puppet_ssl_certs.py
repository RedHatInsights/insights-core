from falafel.mappers.puppet_ssl_certs import PuppetSSLCertCA
from falafel.tests import context_wrap

CAPEM = "..."  # we do not care about the content of this file


def test_ca_pem():
    data = PuppetSSLCertCA(context_wrap(CAPEM))
    assert data is not None
