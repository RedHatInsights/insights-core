import doctest
import pytest

from insights.parsers import ssl_certificate, ParseException, SkipException
from insights.core.plugins import ContentException
from insights.tests import context_wrap


CERTIFICATE_OUTPUT1 = """
issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com
notBefore=Dec  7 07:02:33 2020 GMT
notAfter=Jan 18 07:02:33 2038 GMT
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com
"""

CERTIFICATE_CHAIN_OUTPUT1 = """
issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.b.com
notBefore=Dec  7 07:02:33 2020 GMT
notAfter=Jan 18 07:02:33 2038 GMT


issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.d.com
subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com
notBefore=Nov 30 07:02:42 2020 GMT
notAfter=Jan 18 07:02:43 2018 GMT
"""

CERTIFICATE_CHAIN_OUTPUT2 = """
notAfter=Dec  4 07:04:05 2035 GMT
subject= /CN=Puppet CA: abc.d.com
issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=abc.d.com
"""

SATELLITE_OUTPUT1 = """
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
notAfter=Jan 18 07:02:33 2038 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
notAfter=Jan 18 07:02:43 2018 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com
notAfter=Jan 18 07:02:43 2048 GMT
"""

SATELLITE_OUTPUT2 = """
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
notAfter=Jan 18 07:02:33 2038 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
notAfter=Jan 18 07:02:43 2028 GMT
"""

RHSM_KATELLO_CERT_OUTPUT1 = """
issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com
"""

BAD_OUTPUT1 = """
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
notAfterJan 18 07:02:33 2038 GMT
"""

BAD_OUTPUT2 = """
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
notAfter=2038 Jan 18 07:02:33 GMT
"""

BAD_OUTPUT3 = """
Error opening Certificate /etc/rhsm/ca/katello-default-ca.pem
139814540982160:error:02001002:system library:fopen:No such file or directory:bss_file.c:402:fopen('/etc/rhsm/ca/katello-default-ca.pem','r')
139814540982160:error:20074002:BIO routines:FILE_CTRL:system lib:bss_file.c:404:
unable to load certificate
"""

BAD_OUTPUT4 = """

"""


def test_certificate_info_exception():
    with pytest.raises(ParseException):
        ssl_certificate.CertificateInfo(context_wrap(BAD_OUTPUT1))
    with pytest.raises(ParseException):
        ssl_certificate.CertificateInfo(context_wrap(BAD_OUTPUT2))
    with pytest.raises(ContentException):
        ssl_certificate.CertificateInfo(context_wrap(BAD_OUTPUT3))
    with pytest.raises(SkipException):
        ssl_certificate.CertificateInfo(context_wrap(BAD_OUTPUT4))


def test_certificate_chain_exception():
    with pytest.raises(SkipException):
        ssl_certificate.CertificateChain(context_wrap(BAD_OUTPUT4))


def test_certificate_info():
    cert = ssl_certificate.CertificateInfo(context_wrap(CERTIFICATE_OUTPUT1))
    assert cert['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'
    assert cert['notBefore'].str == 'Dec  7 07:02:33 2020'
    assert cert['notAfter'].str == 'Jan 18 07:02:33 2038'
    assert cert['subject'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'


def test_certificates_chain():
    certs = ssl_certificate.CertificateChain(context_wrap(CERTIFICATE_CHAIN_OUTPUT1))
    assert len(certs) == 2
    assert certs.earliest_expiry_date.str == 'Jan 18 07:02:43 2018'
    for cert in certs:
        if cert['notAfter'].str == certs.earliest_expiry_date.str:
            assert cert['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.d.com'
            assert cert['notBefore'].str == 'Nov 30 07:02:42 2020'
            assert cert['subject'] == '/C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com'
            assert cert['notBefore'].str == 'Nov 30 07:02:42 2020'

    certs = ssl_certificate.CertificateChain(context_wrap(CERTIFICATE_CHAIN_OUTPUT2))
    assert len(certs) == 1
    assert certs[0]['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=abc.d.com'

    certs = ssl_certificate.CertificateChain(context_wrap(RHSM_KATELLO_CERT_OUTPUT1))
    assert len(certs) == 1


def test_satellite_ca_chain():
    certs = ssl_certificate.SatelliteCustomCaChain(context_wrap(SATELLITE_OUTPUT1))
    assert len(certs) == 3
    assert certs.earliest_expiry_date.str == 'Jan 18 07:02:43 2018'
    assert certs[0]['subject'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com'
    assert certs[0]['notAfter'].str == 'Jan 18 07:02:33 2038'
    assert certs[1]['subject'] == '/C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com'
    assert certs[1]['notAfter'].str == 'Jan 18 07:02:43 2018'
    assert certs[2]['subject'] == '/C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com'
    assert certs[2]['notAfter'].str == 'Jan 18 07:02:43 2048'


def test_rhsm_katello_default_ca():
    rhsm_katello_default_ca = ssl_certificate.RhsmKatelloDefaultCACert(context_wrap(RHSM_KATELLO_CERT_OUTPUT1))
    assert rhsm_katello_default_ca['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'


def test_doc():
    cert = ssl_certificate.CertificateInfo(context_wrap(CERTIFICATE_OUTPUT1))
    ca_cert = ssl_certificate.CertificateChain(context_wrap(CERTIFICATE_CHAIN_OUTPUT1))
    satellite_ca_certs = ssl_certificate.SatelliteCustomCaChain(context_wrap(SATELLITE_OUTPUT2))
    rhsm_katello_default_ca = ssl_certificate.RhsmKatelloDefaultCACert(context_wrap(RHSM_KATELLO_CERT_OUTPUT1))

    globs = {
        'cert': cert,
        'certs': ca_cert,
        'satellite_ca_certs': satellite_ca_certs,
        'rhsm_katello_default_ca': rhsm_katello_default_ca
    }
    failed, tested = doctest.testmod(ssl_certificate, globs=globs)
    assert failed == 0
