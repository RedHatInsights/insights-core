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
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 5556 (0x15b4)
        Signature Algorithm: PKCS #1 SHA-256 With RSA Encryption
        Issuer: "CN=Certificate Shack,O=huali.node2.redhat.com,C=CN"
        Validity:
            Not Before: Tue Dec 07 05:26:10 2021
            Not After : Sun Dec 07 05:26:10 2025
        Subject: "CN=huali.node2.redhat.com,O=example.com,C=CN"
        Subject Public Key Info:
            Public Key Algorithm: PKCS #1 RSA Encryption
            RSA Public Key:
                Modulus:
                    a9:95:ef:16:0e:e5:3d:52:0f:39:b2:73:34:c1:11:13:
                    80:57:f1:de:ef:d5:c5:a0:35:8e:2f:4f:e8:25:1c:7f:
                    c0:04:89:b9:bb:6a:af:df:2a:fd:ff:d4:2f:d5:76:16:
                    af:68:b9:8c:a3:72:a2:12:fb:a3:53:48:85:44:c2:57:
                    ce:aa:b7:b2:1e:fb:44:48:97:82:cd:d5:8c:cc:d4:cb:
                    40:91:17:6a:65:97:95:0b:0d:07:c0:19:40:0f:13:73:
                    53:2d:b2:c1:18:01:ad:f5:90:65:64:17:19:cf:00:4d:
                    f7:72:97:50:2e:11:d8:f0:98:d0:35:03:db:15:b7:41:
                    c5:92:5c:13:74:57:60:4c:d3:15:2a:67:ea:ad:01:77:
                    f5:6c:51:cb:68:28:e7:fa:d5:9b:35:d8:f3:a1:82:e3:
                    d5:92:9b:eb:ce:7b:e4:9f:80:5a:31:7f:4a:9b:98:4b:
                    bf:34:2e:c8:06:5c:dc:a7:7f:15:48:49:d0:ab:e4:b5:
                    52:10:22:24:e1:61:26:80:46:55:c7:2a:2b:9c:38:c8:
                    bf:7f:46:e2:e0:12:cc:80:0d:4c:56:12:ca:6c:c6:28:
                    17:fe:89:f0:57:f4:c7:83:f1:5e:57:c1:b2:70:66:28:
                    50:a3:81:84:46:2a:39:c7:a8:ac:a0:c3:c8:fe:bb:d3
                Exponent: 65537 (0x10001)
        Signed Extensions:
            Name: Certificate Type
            Data: <SSL Server>

            Name: Certificate Key Usage
            Usages: Key Encipherment

    Signature Algorithm: PKCS #1 SHA-256 With RSA Encryption
    Signature:
        32:49:6c:67:8f:ea:eb:49:b9:0d:8c:74:fa:08:7b:f5:
        90:51:2a:a9:ff:8d:27:c6:f3:5d:0d:6a:b9:b1:03:f2:
        2c:85:f2:3a:4f:1b:79:37:a9:c1:05:b0:4a:48:84:ef:
        31:45:19:02:db:93:71:72:72:2f:8f:df:aa:e6:4b:b6:
        15:f4:69:41:d4:73:af:67:ab:ac:4e:36:ff:42:d4:69:
        4c:db:1b:91:85:8d:62:b8:62:fc:35:2c:39:c2:58:f9:
        26:05:3a:b0:b8:96:4e:3d:90:7b:05:8e:da:aa:8f:e4:
        61:87:b0:98:4f:02:5e:8a:70:5b:34:82:93:a0:cc:10:
        fd:a6:57:90:dc:e5:43:89:70:3f:eb:06:56:26:78:a8:
        8b:77:85:fb:14:30:74:57:86:5f:58:e7:f6:f8:23:5b:
        1a:72:13:9d:31:f7:ed:d6:0a:13:b0:07:5b:30:c4:67:
        3b:e5:5a:1b:1d:80:b6:ba:21:f5:f9:56:76:81:9d:40:
        83:2c:a5:02:62:e6:ef:25:5f:1c:e8:7d:46:11:0c:76:
        bc:06:84:4f:d3:50:65:fe:5c:40:63:f1:aa:30:72:69:
        27:0d:01:8a:54:ef:7d:ad:d0:a3:73:c8:76:cc:65:14:
        8a:9d:3d:b7:98:b7:be:53:77:d4:65:44:87:5f:3b:6c
    Fingerprint (SHA-256):
        9E:A9:41:42:B3:B7:11:B8:59:4C:FA:66:44:24:91:E3:B6:2F:21:AB:29:BE:26:AB:D3:D7:FA:49:1B:59:EA:AB
    Fingerprint (SHA1):
        E5:E3:BE:30:7E:F9:AD:E7:B4:1E:76:74:1B:2E:EC:4D:AD:1A:9B:A3

    Mozilla-CA-Policy: false (attribute missing)
    Certificate Trust Flags:
        SSL Flags:
            User
        Email Flags:
            User
        Object Signing Flags:
            User
""".strip()

NSS_CERT_BAD_OUTPUT_1 = """
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 5556 (0x15b4)
        Signature Algorithm: PKCS #1 SHA-256 With RSA Encryption
        Issuer: "CN=Certificate Shack,O=huali.node2.redhat.com,C=CN"
        Validity:
            Not Before: Tue Dec 07 05:26:10 2021
            Not After : Dec 07 05:26:10 2025
        Subject: "CN=huali.node2.redhat.com,O=example.com,C=CN"
""".strip()

NSS_CERT_BAD_OUTPUT_2 = """
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 5556 (0x15b4)
        Signature Algorithm: PKCS #1 SHA-256 With RSA Encryption
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
