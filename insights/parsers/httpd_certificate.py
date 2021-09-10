"""
HttpdSSLCertExpireDate - command ``openssl x509 -in httpd_certificate_path -enddate -noout``
============================================================================================

The HttpdSSLCertExpireDate parser reads the output of
``openssl x509 -in httpd_certificate_path -enddate -noout``.

Sample output of ``openssl x509 -in httpd_certificate_path -enddate -noout``::

    notAfter=Dec 4 07:04:05 2035 GMT

Examples:

    >>> type(date_info)
    <class 'insights.parsers.httpd_certificate.HttpdSSLCertExpireDate'>
    >>> date_info['notAfter'].datetime
    datetime.datetime(2038, 1, 18, 7, 2, 43)

"""

from insights import parser
from insights.specs import Specs
from insights.parsers.ssl_certificate import CertificateInfo


@parser(Specs.httpd_ssl_cert_enddate)
class HttpdSSLCertExpireDate(CertificateInfo):
    """
    .. note::
        Please refer to its super-class :class:`insights.parsers.ssl_certificate.CertificateInfo` for more
        details.

    Parse the output of ``openssl x509 -in httpd_ssl_certificate_path -enddate -noout``
    """
    pass
