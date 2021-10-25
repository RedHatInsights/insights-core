import doctest
import pytest

from insights.combiners import ssl_certificate
from insights.combiners.ssl_certificate import EarliestNginxSSLCertExpireDate
from insights.core.dr import SkipComponent
from insights.tests import context_wrap


NGINX_CERT_EXPIRE_INFO_1 = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''

NGINX_CERT_EXPIRE_INFO_2 = '''
notAfter=Dec 18 07:02:43 2021 GMT
'''


def test_nginx_ssl_cert_combiner():
    date_info = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    expiredate_obj = EarliestNginxSSLCertExpireDate([date_info])
    assert expiredate_obj.earliest_expire_date
    expired_date, cert_path = expiredate_obj.earliest_expire_date
    assert expired_date == 'Jan 18 07:02:43 2038'
    assert cert_path == '/test/c.pem'

    date_info1 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    date_info2 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_2, args='/test/d.pem'))
    expiredate_obj = EarliestNginxSSLCertExpireDate([date_info1, date_info2])
    assert expiredate_obj.earliest_expire_date
    expired_date, cert_path = expiredate_obj.earliest_expire_date
    assert expired_date == 'Dec 18 07:02:43 2021'
    assert cert_path == '/test/d.pem'


def test_doc():
    date_info1 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_1, args='/test/c.pem'))
    date_info2 = ssl_certificate.NginxSSLCertExpireDate(context_wrap(NGINX_CERT_EXPIRE_INFO_2, args='/test/d.pem'))
    nginx_certs = EarliestNginxSSLCertExpireDate([date_info1, date_info2])
    globs = {
        'nginx_certs': nginx_certs
    }
    failed, _ = doctest.testmod(ssl_certificate, globs=globs)
    assert failed == 0


def test_nginx_ssl_certs_combiner_exception():
    with pytest.raises(SkipComponent):
        date_info = EarliestNginxSSLCertExpireDate([])
        date_info.earliest_expire_date
