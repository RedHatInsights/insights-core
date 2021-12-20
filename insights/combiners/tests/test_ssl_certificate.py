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
            Not After : Sun Dec 07 05:26:10 2025"""

HTTPD_CERT_EXPIRED_INFO_IN_NSS_2 = """
            Not After : Sun Jan 07 05:26:10 2022"""


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
