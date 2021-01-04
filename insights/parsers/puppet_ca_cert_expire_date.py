"""
PuppetCertExpireDate - command ``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``
============================================================================================================

The PuppetCertExpireDate parser reads the output of
``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``.

Sample output of ``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``::

    notAfter=Dec  4 07:04:05 2035 GMT

Examples::

    >>> type(date_info)
    <class 'insights.parsers.puppet_ca_cert_expire_date.PuppetCertExpireDate'>
    >>> date_info.expire_date
    datetime.datetime(2035, 12, 4, 7, 4, 5)

"""
from datetime import datetime

from insights import parser, CommandParser
from insights.specs import Specs
from insights.parsers import SkipException, ParseException


@parser(Specs.puppet_ca_cert_expire_date)
class PuppetCertExpireDate(CommandParser):
    """
    Read the ``openssl x509 -in /etc/puppetlabs/puppet/ssl/ca/ca_crt.pem -enddate -noout``
    and set the date to property ``expire_date``.

    Attributes:
        expire_date (datetime): The date when the puppet ca cert will be expired
    """

    def parse_content(self, content):
        if len(content) == 1 and content[0].startswith('notAfter='):
            date_format = '%b %d %H:%M:%S %Y %Z'
            date_str = content[0].split('=', 1)[1]
            try:
                self.expire_date = datetime.strptime(date_str, date_format)
            except Exception:
                raise ParseException("Can not parse the date format")
        else:
            raise SkipException("Cannot get the puppet ca cert expire info")
