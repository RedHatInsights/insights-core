import pytest
import doctest

from insights.parsers import rhc_conf
from insights.parsers.rhc_conf import RHCConf
from insights.tests import context_wrap
from insights.core.dr import SkipComponent


RHC_CONFIG = """
# rhc global configuration settings

broker = ["wss://connect.cloud.redhat.com:443"]
cert-file = "/etc/pki/consumer/cert.pem"
"key-file" = "/etc/pki/consumer/key.pem"
invalid lines
log-level = "error"
""".strip()

RHC_EMPTY_CONFIG = """
# rhc global configuration settings
""".strip()


def test_doc():
    failed, _ = doctest.testmod(rhc_conf, globs={
        'rhc_conf': RHCConf(context_wrap(RHC_CONFIG))
    })
    assert failed == 0


def test_rhc_conf():
    rhc = RHCConf(context_wrap(RHC_CONFIG))
    assert len(rhc) == 4
    assert rhc['log-level'] == 'error'
    assert rhc['key-file'] == '/etc/pki/consumer/key.pem'
    assert rhc['cert-file'] == "/etc/pki/consumer/cert.pem"
    assert rhc['broker'] == '["wss://connect.cloud.redhat.com:443"]'


def test_exception():
    with pytest.raises(SkipComponent):
        RHCConf(context_wrap(RHC_EMPTY_CONFIG))
