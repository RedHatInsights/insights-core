"""
Combiners for getting the earliest expiry date from a lot of SSL certificates
=============================================================================

This module contains the following combiners:

EarliestNginxSSLCertExpireDate - The earliest expire date in a lot of nginx ssl certificates
--------------------------------------------------------------------------------------------
Combiner to get the earliest expire date in a lot of nginx ssl certificates.

EarliestHttpdSSLCertExpireDate - The earliest expire date in a lot of httpd ssl certificates
--------------------------------------------------------------------------------------------
Combiner to get the earliest expire date in a lot of httpd ssl certificates.

EarliestHttpdCertInNSSExpireDate - The earliest expire date in a lot of httpd certificates stored in nss database
-----------------------------------------------------------------------------------------------------------------
Combiner to get the earliest expire date in a lot of httpd certificates stored in nss database.
"""
from insights.core.exceptions import SkipComponent
from insights.core.plugins import combiner
from insights.parsers.certificates_enddate import CertificatesEnddate
from insights.parsers.ssl_certificate import HttpdCertInfoInNSS, NginxSSLCertExpireDate, HttpdSSLCertExpireDate


class EarliestSSLCertExpireDate(object):
    """
    The base class to get the earliest expiry date from a lot of :class:`insights.parsers.ssl_certificate.CertificateInfo` instances.

    Attributes:
        earliest_expire_date (str): The earliest expire date in string format.
        ssl_cert_path (str): The SSL certificate path which is expired first.

    Examples:
        >>> type(ssl_certs)
        <class 'insights.combiners.ssl_certificate.EarliestSSLCertExpireDate'>
        >>> ssl_certs.earliest_expire_date.str
        'Dec 18 07:02:43 2021'
        >>> ssl_certs.ssl_cert_path
        '/test/b.pem'
    """
    def __init__(self, certificate_info_list):
        self.earliest_expire_date = None
        self.ssl_cert_path = None
        for ssl_cert_expiry_date in certificate_info_list:
            if (self.earliest_expire_date is None or
                (isinstance(ssl_cert_expiry_date.get('notAfter', ''), CertificatesEnddate.ExpirationDate) and
                    ssl_cert_expiry_date['notAfter'].datetime < self.earliest_expire_date.datetime)):
                self.earliest_expire_date = ssl_cert_expiry_date['notAfter']
                self.ssl_cert_path = ssl_cert_expiry_date.cert_path
        if self.earliest_expire_date is None:
            raise SkipComponent


@combiner(NginxSSLCertExpireDate)
class EarliestNginxSSLCertExpireDate(EarliestSSLCertExpireDate):
    """
    Combiner to get the earliest expire date in a lot of nginx ssl certificates.

    Examples:
        >>> type(nginx_certs)
        <class 'insights.combiners.ssl_certificate.EarliestNginxSSLCertExpireDate'>
        >>> nginx_certs.earliest_expire_date.str
        'Dec 18 07:02:43 2021'
        >>> nginx_certs.ssl_cert_path
        '/test/d.pem'
    """
    pass


@combiner(HttpdSSLCertExpireDate)
class EarliestHttpdSSLCertExpireDate(EarliestSSLCertExpireDate):
    """
    Combiner to get the earliest expire date in a lot of httpd ssl certificates.

    Examples:
        >>> type(httpd_certs)
        <class 'insights.combiners.ssl_certificate.EarliestHttpdSSLCertExpireDate'>
        >>> httpd_certs.earliest_expire_date.str
        'Dec 18 07:02:43 2021'
        >>> httpd_certs.ssl_cert_path
        '/test/d.pem'
    """
    pass


@combiner(HttpdCertInfoInNSS)
class EarliestHttpdCertInNSSExpireDate(EarliestSSLCertExpireDate):
    """
    Combiner to get the earliest expire date in a lot of httpd certificates stored in NSS database.

    Examples:
        >>> type(httpd_certs_in_nss)
        <class 'insights.combiners.ssl_certificate.EarliestHttpdCertInNSSExpireDate'>
        >>> httpd_certs_in_nss.earliest_expire_date.str
        'Sun Jan 07 05:26:10 2022'
        >>> httpd_certs_in_nss.ssl_cert_path
        ('/etc/httpd/nss', 'testcerta')
    """
    pass
