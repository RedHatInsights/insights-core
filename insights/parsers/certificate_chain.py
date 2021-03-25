"""
Get Certificate Chain Info
==========================

This module contains the following parsers:

SatelliteCustomCaChain - command ``awk 'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}' /etc/pki/katello/certs/katello-server-ca.crt``
========================================================================================================================================================================================================================================
"""

from insights import parser, CommandParser
from datetime import datetime
from insights.parsers import ParseException, SkipException
from insights.specs import Specs
from insights.parsers.certificates_enddate import CertificatesEnddate


class CertificateChain(CommandParser, list):
    """
    Class to parse the output of "openssl -in <certificate_chain_file> -xxx -xxx".
    Blank line is added to distinguish different certs in the chain.
    Currently it only supports the attributes which the output is in
    key=value pairs.

    Sample Output::

        issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
        subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.b.com
        notBefore=Dec  7 07:02:33 2020 GMT
        notAfter=Jan 18 07:02:33 2038 GMT

        issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.c.com
        subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.d.com
        notBefore=Nov 30 07:02:42 2020 GMT
        notAfter=Jan 18 07:02:43 2018 GMT

    Examples:
        >>> type(certs)
        <class 'insights.parsers.certificate_chain.CertificateChain'>
        >>> len(certs)
        2
        >>> certs.earliest_expiry_date.str
        'Jan 18 07:02:43 2018'
    """

    expire_date_format = '%b %d %H:%M:%S %Y'

    def parse_content(self, content):
        """
        Parse the content of crt chain file. And it saves the expiration
        info of each crt in a list of dict. The value of notBefore and
        notAfter are saved to an instance of ExpirationDate, it
        contains the date in string and datetime format.

        Attributes:
            earliest_expiry_date(ExpirationDate):
                The earliest expiry datetime of the certs in the chain.
                None when there isn't "notAfter" for all the certs
                in the chain.

        Raises:
            ParseException: when the output isn't in key=value format or
                            the notAfter or notBefore isn't expected format.
        """
        if len(content) < 1:
            raise SkipException("No cert in the output")
        data = {}
        self.append(data)
        self.earliest_expiry_date = None
        for index, line in enumerate(content):
            if not line.strip():
                # a new cert starts
                if data:
                    data = {}
                    self.append(data)
                continue
            if '=' not in line:
                raise ParseException('The line %s is not in key=value format' % line)
            key, value = [item.strip() for item in line.split('=', 1)]
            value_without_tz = value.rsplit(" ", 1)[0]
            if key in ['notBefore', 'notAfter']:
                try:
                    date_time = datetime.strptime(value_without_tz, self.expire_date_format)
                except Exception:
                    raise ParseException('The %s is not in %s format.' % (key, self.expire_date_format))
                value = CertificatesEnddate.ExpirationDate(value_without_tz, date_time)
            data[key] = value

        for one_cert in self:
            expire_date = one_cert.get('notAfter')
            if expire_date and (self.earliest_expiry_date is None or expire_date.datetime < self.earliest_expiry_date.datetime):
                self.earliest_expiry_date = expire_date


@parser(Specs.satellite_custom_ca_chain)
class SatelliteCustomCaChain(CertificateChain):
    """
    .. note::
        Please refer to its super-class :class:`insights.parsers.certificate_chain.CertificateChain` for more
        details.

    Sample Output::

        subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
        notAfter=Jan 18 07:02:33 2038 GMT

        subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
        notAfter=Jan 18 07:02:43 2028 GMT

    Examples:
        >>> type(satellite_ca_certs)
        <class 'insights.parsers.certificate_chain.SatelliteCustomCaChain'>
        >>> len(satellite_ca_certs)
        2
        >>> satellite_ca_certs.earliest_expiry_date.str
        'Jan 18 07:02:43 2028'
    """
    pass
