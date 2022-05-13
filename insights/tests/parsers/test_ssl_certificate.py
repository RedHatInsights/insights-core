import doctest
from insights.core.dr import SkipComponent
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

HTTPD_CERT_EXPIRE_INFO = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''

NGINX_CERT_EXPIRE_INFO = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''

MSSQL_CERT_EXPIRE_INFO = '''
notAfter=Nov  5 01:43:59 2022 GMT
'''

NSS_CERT_OUTPUT = """
        Not After : Sun Dec 07 05:26:10 2025"""

NSS_CERT_BAD_OUTPUT_1 = """
            Not After : Dec 07 05:26:10 2025"""

NSS_CERT_BAD_OUTPUT_2 = """
        Issuer: "CN=Certificate Shack,O=huali.node2.redhat.com,C=CN
""".strip()


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
    cert = ssl_certificate.CertificateInfo(context_wrap(CERTIFICATE_OUTPUT1, args='/a/b/c.pem'))
    assert cert['issuer'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'
    assert cert['notBefore'].str == 'Dec  7 07:02:33 2020'
    assert cert['notAfter'].str == 'Jan 18 07:02:33 2038'
    assert cert['subject'] == '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'
    assert cert.cert_path == '/a/b/c.pem'


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
    date_info = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO))
    nginx_date_info = ssl_certificate.NginxSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO, args='/a/b/c.pem'))
    mssql_date_info = ssl_certificate.MssqlTLSCertExpireDate(context_wrap(MSSQL_CERT_EXPIRE_INFO))
    cert_info = ssl_certificate.HttpdCertInfoInNSS(context_wrap(NSS_CERT_OUTPUT))
    globs = {
        'cert': cert,
        'certs': ca_cert,
        'satellite_ca_certs': satellite_ca_certs,
        'rhsm_katello_default_ca': rhsm_katello_default_ca,
        'date_info': date_info,
        'nginx_date_info': nginx_date_info,
        'mssql_date_info': mssql_date_info,
        'nss_cert_info': cert_info
    }
    failed, _ = doctest.testmod(ssl_certificate, globs=globs)
    assert failed == 0


def test_httpd_ssl_cert_parser():
    date_info = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO))
    assert 'notAfter' in date_info
    assert date_info['notAfter'].str == 'Jan 18 07:02:43 2038'


def test_nginx_ssl_cert_parser():
    date_info = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO, args='/test/c.pem'))
    assert 'notAfter' in date_info
    assert date_info['notAfter'].str == 'Jan 18 07:02:43 2038'
    assert date_info.cert_path == '/test/c.pem'


def test_mssql_tls_cert_parser():
    date_info = ssl_certificate.MssqlTLSCertExpireDate(context_wrap(MSSQL_CERT_EXPIRE_INFO))
    assert 'notAfter' in date_info
    assert date_info['notAfter'].str == 'Nov  5 01:43:59 2022'


def test_httpd_cert_info_in_nss():
    cert_info = ssl_certificate.HttpdCertInfoInNSS(context_wrap(NSS_CERT_OUTPUT))
    assert 'notAfter' in cert_info
    assert cert_info['notAfter'].str == 'Sun Dec 07 05:26:10 2025'


def test_httpd_cert_info_in_nss_exception():
    with pytest.raises(ParseException):
        ssl_certificate.HttpdCertInfoInNSS(context_wrap(NSS_CERT_BAD_OUTPUT_1))

    with pytest.raises(SkipComponent):
        ssl_certificate.HttpdCertInfoInNSS(context_wrap(NSS_CERT_BAD_OUTPUT_2))
