import doctest

from insights.parsers import httpd_certificate
from insights.tests import context_wrap


HTTPD_CERT_EXPIRE_INFO = '''
notAfter=Jan 18 07:02:43 2038 GMT
'''


def test_HTL_doc_examples():
    date_info = httpd_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO))
    globs = {
        'date_info': date_info
    }
    failed, tested = doctest.testmod(httpd_certificate, globs=globs)
    assert failed == 0


def test_parser():
    date_info = httpd_certificate.HttpdSSLCertExpireDate(context_wrap(HTTPD_CERT_EXPIRE_INFO))
    assert 'notAfter' in date_info
    assert date_info['notAfter'].str == 'Jan 18 07:02:43 2038'
