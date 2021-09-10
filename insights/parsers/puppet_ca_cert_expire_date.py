"""
PuppetCertExpireDate - command ``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``
============================================================================================================

. warning::
   This Parser is deprecated, please use the
   :class:`insights.parsers.ssl_certificate.CertificatesInfo` instead.

The PuppetCertExpireDate parser reads the output of
``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``.

Sample output of ``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``::

    notAfter=Dec  4 07:04:05 2035 GMT

Examples::

    >>> type(date_info)
    <class 'insights.parsers.puppet_ca_cert_expire_date.PuppetCertExpireDate'>
    >>> date_info['notAfter'].datetime
    datetime.datetime(2035, 12, 4, 7, 4, 5)

"""

from insights import parser
from insights.specs import Specs
from insights.parsers import SkipException
from insights.parsers.ssl_certificate import CertificateInfo
from insights.util import deprecated


@parser(Specs.puppet_ca_cert_expire_date)
class PuppetCertExpireDate(CertificateInfo):
    """
    .. warning::
        This Parser is deprecated, please use the
        :class:`insights.parsers.ssl_certificate.CertificatesInfo` instead.

    .. note::
        Please refer to its super-class :class:`insights.parsers.ssl_certificate.CertificateInfo` for more
        details.

    .. warning::
        The attribute expire_date is deprecated, please get the value from the dictionary directly instead.

    Read the ``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``
    and set the date to property ``expire_date``.

    Attributes:
        expire_date (datetime): The date when the puppet ca cert will be expired

    Raises:
        SkipException: when notAfter isn't in the output
    """
    def __init__(self, *args, **kwargs):
        deprecated(PuppetCertExpireDate, "Import 'insights.parsers.ssl_certificate.CertificatesInfo' instead.")
        super(PuppetCertExpireDate, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        super(PuppetCertExpireDate, self).parse_content(content)
        if 'notAfter' not in self:
            raise SkipException("Cannot get the puppet ca cert expire info")
        self.expire_date = self['notAfter'].datetime
