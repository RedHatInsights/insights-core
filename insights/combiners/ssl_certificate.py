"""
Combiners for getting the earliest expiry date from a lot of SSL certificates
=============================================================================

This module contains the following combiners:

EarliestNginxSSLCertExpireDate - The earliest expire date of nginx ssl certificates
-----------------------------------------------------------------------------------
Combiner to get the earliest expire date of nginx ssl certificates.
"""

from insights.parsers.ssl_certificate import NginxSSLCertExpireDate
from insights.parsers.certificates_enddate import CertificatesEnddate
from insights.core.plugins import combiner
from insights.core.dr import SkipComponent


class EarliestSSLCertExpireDate(object):
    """
    The base class to get the earliest expiry date from a lot of CertificateInfo instances.

    .. note::
        Please refer to :class:`insights.parsers.ssl_certificate.CertificateInfo` for more
        details.
    """
    def __init__(self, ssl_cert_expiry_date_list):
        self.ssl_cert_expiry_date_list = ssl_cert_expiry_date_list

    @property
    def earliest_expire_date(self):
        '''
        Return the earliest expiry date and the corresponding SSL certificate path.

        Raises:
            SkipComponent: when can not find expiry date info from the ssl certificate list.
        '''
        earliest_date = None
        ssl_cert_path = None
        for ssl_cert_expiry_date in self.ssl_cert_expiry_date_list:
            if (earliest_date is None or
                (isinstance(ssl_cert_expiry_date.get('notAfter', ''), CertificatesEnddate.ExpirationDate) and
                    ssl_cert_expiry_date['notAfter'].datetime < earliest_date.datetime)):
                earliest_date = ssl_cert_expiry_date['notAfter']
                ssl_cert_path = ssl_cert_expiry_date.cert_path
        if earliest_date:
            return earliest_date.str, ssl_cert_path
        raise SkipComponent


@combiner(NginxSSLCertExpireDate)
class EarliestNginxSSLCertExpireDate(EarliestSSLCertExpireDate):
    """
    .. note::
        Please refer to its super-class :class:`insights.combiners.ssl_certificate.EarliestSSLCertExpireDate` for more
        details.

    Examples:
        >>> type(nginx_certs)
        <class 'insights.combiners.ssl_certificate.EarliestNginxSSLCertExpireDate'>
        >>> expire_date, file_path = nginx_certs.earliest_expire_date
        >>> expire_date
        'Dec 18 07:02:43 2021'
        >>> file_path
        '/test/d.pem'
    """
    pass
