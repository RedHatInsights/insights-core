"""
Get Certificate Chain Endates
=============================

This module contains the following parsers:

SatelliteCustomCaChain - command ``awk 'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}' /etc/pki/katello/certs/katello-server-ca.crt``
========================================================================================================================================================================================================================================
"""

from insights import parser, CommandParser
from datetime import datetime
from insights.parsers import ParseException
from insights.specs import Specs
from insights.parsers.certificates_enddate import ExpirationDate


class CertificateChainEnddates(CommandParser, list):
    """
    Class to parse the expiration dates of a certificate chain file.
    Blank line is added to distinguish different certs.
    Currently it only supports the output in key=value pairs.

    Sample Output::

        issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
        subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.b.com
        notBefore=Dec  7 07:02:33 2020 GMT
        notAfter=Jan 18 07:02:33 2038 GMT

        issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.c.com
        subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.d.com
        notBefore=Nov 30 07:02:42 2020 GMT
        notAfter=Jan 18 07:02:43 2018 GMT

    Examples::

        >>> type(certs)
        <class 'insights.parsers.certificate_chain_enddates.CertificateChainEnddates'>
        >>> len(certs)
        2
        >>> certs.earliest_expiration_date.str
        'Jan 18 07:02:43 2018 GMT'
    """

    expire_date_format = '%b %d %H:%M:%S %Y'

    def parse_content(self, content):
        """
        Parse the content of crt chain file. And it saves the expiration
        info of each crt in a list of dict.

        Raises::

            ParseException: when the output isn't in key=value format or
                            the notAfter or notBefore isn't expected format.
        """
        for index, line in enumerate(content):
            if index == 0:
                data = {}
            if not line.strip():
                # a new cert starts
                self.append(data)
                data = {}
                continue
            if '=' not in line:
                raise ParseException('The line %s is not in key=value format' % line)
            key, value = [item.strip() for item in line.split('=', 1)]
            if key in ['notBefore', 'notAfter']:
                try:
                    date_time = datetime.strptime(value.rsplit(" ", 1)[0], self.expire_date_format)
                except Exception:
                    raise ParseException('The %s is not in %s format.' % (key, self.expire_date_format))
                value = ExpirationDate(value, date_time)
            data[key] = value
            if index == len(content) - 1:
                # append the last cert
                self.append(data)

    @property
    def earliest_expiration_date(self):
        """This will return the earliest expiration date or None if notAfter not found"""
        earliest_date = None
        for one_cert in self:
            expire_date = one_cert.get('notAfter')
            if expire_date and (earliest_date is None or expire_date.datetime < earliest_date.datetime):
                earliest_date = expire_date
        return earliest_date


@parser(Specs.satellite_custom_ca_chain)
class SatelliteCustomCaChain(CertificateChainEnddates):
    """
    .. note::
        Please refer to its super-class :class:`insights.parsers.certificate_chain_enddates.CertificateChainEnddates` for more
        details.

    Sample Output::

        subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
        notAfter=Jan 18 07:02:33 2038 GMT

        subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
        notAfter=Jan 18 07:02:43 2028 GMT

    Examples::

        >>> type(satellite_ca_certs)
        <class 'insights.parsers.certificate_chain_enddates.SatelliteCustomCaChain'>
        >>> len(satellite_ca_certs)
        2
        >>> satellite_ca_certs.earliest_expiration_date.str
        'Jan 18 07:02:43 2028 GMT'
    """
    pass
