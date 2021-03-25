import doctest
import pytest

from insights.parsers import certificate_chain, ParseException, SkipException
from insights.tests import context_wrap


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

OUTPUT1 = """
issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.b.com
notBefore=Dec  7 07:02:33 2020 GMT
notAfter=Jan 18 07:02:33 2038 GMT

issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.d.com
subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com
notBefore=Nov 30 07:02:42 2020 GMT
notAfter=Jan 18 07:02:43 2018 GMT

"""

OUTPUT2 = """
notAfter=Dec  4 07:04:05 2035 GMT
subject= /CN=Puppet CA: abc.d.com
issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=abc.d.com
"""

BAD_OUTPUT1 = """
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
notAfterJan 18 07:02:33 2038 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
notAfterJan 18 07:02:43 2018 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com
notAfterJan 18 07:02:43 2048 GMT

"""

BAD_OUTPUT2 = """
subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
notAfter=2038 Jan 18 07:02:33 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
notAfterJan 18 07:02:43 2018 GMT

subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com
notAfterJan 18 07:02:43 2048 GMT

"""

BAD_OUTPUT3 = """

"""


def test_certificates_chain():
    certs = certificate_chain.SatelliteCustomCaChain(context_wrap(OUTPUT1))
    assert len(certs) == 2
    assert certs.earliest_expiry_date.str == 'Jan 18 07:02:43 2018'
    for cert in certs:
        if cert['notAfter'].str == certs.earliest_expiry_date.str:
            assert cert['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.d.com'
            assert cert['notBefore'].str == 'Nov 30 07:02:42 2020'
            assert cert['subject'] == '/C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.c.com'
            assert cert['notBefore'].str == 'Nov 30 07:02:42 2020'

    certs = certificate_chain.SatelliteCustomCaChain(context_wrap(OUTPUT2))
    assert len(certs) == 1
    assert certs[0]['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=abc.d.com'


def test_satellite_ca_chain():
    certs = certificate_chain.CertificateChain(context_wrap(SATELLITE_OUTPUT1))
    assert len(certs) == 3
    assert certs.earliest_expiry_date.str == 'Jan 18 07:02:43 2018'
    for cert in certs:
        if cert['notAfter'].str == certs.earliest_expiry_date.str:
            assert cert['subject'] == '/C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com'


def test_doc():
    certs = certificate_chain.CertificateChain(context_wrap(OUTPUT1))
    satellite_ca_certs = certificate_chain.SatelliteCustomCaChain(context_wrap(SATELLITE_OUTPUT2))
    globs = {
        'certs': certs,
        'satellite_ca_certs': satellite_ca_certs
    }
    failed, tested = doctest.testmod(certificate_chain, globs=globs)
    assert failed == 0


def test_certificates_chain_except():
    with pytest.raises(ParseException):
        certificate_chain.CertificateChain(context_wrap(BAD_OUTPUT1))
    with pytest.raises(ParseException):
        certificate_chain.CertificateChain(context_wrap(BAD_OUTPUT2))
    with pytest.raises(SkipException):
        certificate_chain.SatelliteCustomCaChain(context_wrap(BAD_OUTPUT3))
