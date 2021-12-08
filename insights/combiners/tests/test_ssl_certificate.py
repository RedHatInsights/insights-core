import doctest
import pytest

from insights.combiners import ssl_certificate
from insights.parsers.ssl_certificate import CertificateInfo
from insights.core.dr import SkipComponent
from insights.tests import context_wrap


COMMON_SSL_CERT_INFO1 = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''

COMMON_SSL_CERT_INFO2 = '''
notAfter=Dec 18 07:02:43 2021 GMT
'''

NGINX_CERT_EXPIRE_INFO_1 = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''

NGINX_CERT_EXPIRE_INFO_2 = '''
notAfter=Dec 18 07:02:43 2021 GMT
'''

HTTPD_CERT_EXPIRE_INFO_1 = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''

HTTPD_CERT_EXPIRE_INFO_2 = '''
notAfter=Dec 18 07:02:43 2021 GMT
'''

HTTPD_CERT_EXPIRED_INFO_IN_NSS_1 = """
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

HTTPD_CERT_EXPIRED_INFO_IN_NSS_2 = """
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 5556 (0x15b4)
        Signature Algorithm: PKCS #1 SHA-256 With RSA Encryption
        Issuer: "CN=Certificate Shack,O=huali.node2.redhat.com,C=CN"
        Validity:
            Not Before: Tue Dec 07 05:26:10 2021
            Not After : Sun Jan 07 05:26:10 2022
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


def test_earliest_ssl_expire_date():
    date_info1 = CertificateInfo(context_wrap(COMMON_SSL_CERT_INFO1, args='/test/a.pem'))
    date_info2 = CertificateInfo(context_wrap(COMMON_SSL_CERT_INFO2, args='/test/b.pem'))
    expiredate_obj = ssl_certificate.EarliestSSLCertExpireDate([date_info1, date_info2])
    assert expiredate_obj.earliest_expire_date.str == 'Dec 18 07:02:43 2021'
    assert expiredate_obj.ssl_cert_path == '/test/b.pem'


def test_earliest_certs_combiner_exception():
    with pytest.raises(SkipComponent):
        ssl_certificate.EarliestSSLCertExpireDate([])


def test_doc():
    date_info1 = CertificateInfo(context_wrap(COMMON_SSL_CERT_INFO1, args='/test/a.pem'))
    date_info2 = CertificateInfo(context_wrap(COMMON_SSL_CERT_INFO2, args='/test/b.pem'))
    ssl_certs = ssl_certificate.EarliestSSLCertExpireDate([date_info1, date_info2])
    date_info1 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    date_info2 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_2, args='/test/d.pem'))
    nginx_certs = ssl_certificate.EarliestNginxSSLCertExpireDate([date_info1, date_info2])
    date_info1 = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    date_info2 = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO_2, args='/test/d.pem'))
    httpd_certs = ssl_certificate.EarliestHttpdSSLCertExpireDate([date_info1, date_info2])
    date_info1 = ssl_certificate.HttpdCertInfoInNSS(context_wrap(HTTPD_CERT_EXPIRED_INFO_IN_NSS_1, args=('/etc/httpd/nss', 'testcertb')))
    date_info2 = ssl_certificate.HttpdCertInfoInNSS(context_wrap(HTTPD_CERT_EXPIRED_INFO_IN_NSS_2, args=('/etc/httpd/nss', 'testcerta')))
    httpd_certs_in_nss = ssl_certificate.EarliestHttpdCertInNSSExpireDate([date_info1, date_info2])
    globs = {
        'ssl_certs': ssl_certs,
        'nginx_certs': nginx_certs,
        'httpd_certs': httpd_certs,
        'httpd_certs_in_nss': httpd_certs_in_nss
    }
    failed, _ = doctest.testmod(ssl_certificate, globs=globs)
    assert failed == 0


def test_nginx_ssl_cert_combiner():
    date_info = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    expiredate_obj = ssl_certificate.EarliestNginxSSLCertExpireDate([date_info])
    assert expiredate_obj.earliest_expire_date.str == 'Jan 18 07:02:43 2038'
    assert expiredate_obj.ssl_cert_path == '/test/c.pem'

    date_info1 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    date_info2 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_2, args='/test/d.pem'))
    expiredate_obj = ssl_certificate.EarliestNginxSSLCertExpireDate([date_info1, date_info2])
    assert expiredate_obj.earliest_expire_date.str == 'Dec 18 07:02:43 2021'
    assert expiredate_obj.ssl_cert_path == '/test/d.pem'


def test_httpd_ssl_cert_combiner():
    date_info = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    expiredate_obj = ssl_certificate.EarliestHttpdSSLCertExpireDate([date_info])
    assert expiredate_obj.earliest_expire_date.str == 'Jan 18 07:02:43 2038'
    assert expiredate_obj.ssl_cert_path == '/test/c.pem'

    date_info1 = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    date_info2 = ssl_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO_2, args='/test/d.pem'))
    expiredate_obj = ssl_certificate.EarliestHttpdSSLCertExpireDate([date_info1, date_info2])
    assert expiredate_obj.earliest_expire_date.str == 'Dec 18 07:02:43 2021'
    assert expiredate_obj.ssl_cert_path == '/test/d.pem'


def test_httpd_cert_in_nss_combiner():
    date_info1 = ssl_certificate.HttpdCertInfoInNSS(context_wrap(HTTPD_CERT_EXPIRED_INFO_IN_NSS_1, args=('/etc/httpd/nss', 'testcertb')))
    date_info2 = ssl_certificate.HttpdCertInfoInNSS(context_wrap(HTTPD_CERT_EXPIRED_INFO_IN_NSS_2, args=('/etc/httpd/nss', 'testcerta')))
    expiredate_obj = ssl_certificate.EarliestHttpdSSLCertExpireDate([date_info1, date_info2])
    assert expiredate_obj.earliest_expire_date.str == 'Sun Jan 07 05:26:10 2022'
    assert expiredate_obj.ssl_cert_path == ('/etc/httpd/nss', 'testcerta')
