"""
Get SSL Certificate Info
========================

This module contains the following parsers:

SatelliteCustomCaChain - command ``awk 'BEGIN { pipe="openssl x509 -noout -subject -enddate"} /^-+BEGIN CERT/,/^-+END CERT/ { print | pipe } /^-+END CERT/ { close(pipe); printf("\\n")}' /etc/pki/katello/certs/katello-server-ca.crt``
========================================================================================================================================================================================================================================
RhsmKatelloDefaultCACert - command ``openssl x509 -in /etc/rhsm/ca/katello-default-ca.pem -noout -issuer``
==========================================================================================================
"""

from insights import parser, CommandParser
from datetime import datetime
from insights.parsers import ParseException, SkipException
from insights.specs import Specs
from insights.core.context import Context
from insights.parsers.certificates_enddate import CertificatesEnddate


class CertificateInfo(CommandParser, dict):
    """
    Base class to parse the output of "openssl -in <single_certificate_file> -xxx".
    Currently it only supports the attributes which the output is in
    key=value pairs. It saves the cert info into a dict. The value of notBefore and
    notAfter are saved to an instance of ExpirationDate, which contains the date
    in string and datetime format.

    Sample Output::

        issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com
        notBefore=Dec  7 07:02:33 2020 GMT
        notAfter=Jan 18 07:02:33 2038 GMT
        subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com

    Examples:
        >>> type(cert)
        <class 'insights.parsers.ssl_certificate.CertificateInfo'>
        >>> 'issuer' in cert
        True
        >>> cert['issuer']
        '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'
        >>> cert['notBefore'].str
        'Dec  7 07:02:33 2020'

    Raises:
        ParseException: when the output isn't in key=value format or
                        the notAfter or notBefore isn't expected format.
        SkipException: when the content is empty.
    """
    date_format = '%b %d %H:%M:%S %Y'

    def __init__(self, context):
        super(CertificateInfo, self).__init__(
            context,
            extra_bad_lines=['error opening certificate', 'unable to load certificate'])

    def parse_content(self, content):
        if len(content) < 1:
            raise SkipException("No cert in the output")
        for line in content:
            if '=' not in line:
                raise ParseException('The line %s is not in key=value format' % line)
            key, value = [item.strip() for item in line.split('=', 1)]
            if key in ['notBefore', 'notAfter']:
                value_without_tz = value.rsplit(" ", 1)[0]
                try:
                    date_time = datetime.strptime(value_without_tz, self.date_format)
                except Exception:
                    raise ParseException('The %s is not in %s format.' % (key, self.date_format))
                value = CertificatesEnddate.ExpirationDate(value_without_tz, date_time)
            self[key] = value


class CertificateChain(CommandParser, list):
    """
    Base class to parse the output of "openssl -in <certificate_chain_file> -xxx".
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
        <class 'insights.parsers.ssl_certificate.CertificateChain'>
        >>> len(certs)
        2
        >>> certs.earliest_expiry_date.str
        'Jan 18 07:02:43 2018'
    """

    def parse_content(self, content):
        """
        Parse the content of cert chain file. And it saves the certs
        in a list of dict. Each cert is saved as an CertificateInfo
        instance.

        Attributes:
            earliest_expiry_date(ExpirationDate):
                The earliest expiry datetime of the certs in the chain.
                None when there isn't "notAfter" for all the certs
                in the chain.
        """

        self.earliest_expiry_date = None
        start_index = 0
        for index, line in enumerate(content):
            if not line.strip():
                self.append(CertificateInfo(Context(content=content[start_index:index], path=None)))
                start_index = index + 1
            if index == len(content) - 1:
                self.append(CertificateInfo(Context(content=content[start_index:index + 1], path=None)))
        for one_cert in self:
            expire_date = one_cert.get('notAfter')
            if expire_date and (self.earliest_expiry_date is None or expire_date.datetime < self.earliest_expiry_date.datetime):
                self.earliest_expiry_date = expire_date


@parser(Specs.satellite_custom_ca_chain)
class SatelliteCustomCaChain(CertificateChain):
    """
    .. note::
        Please refer to its super-class :class:`insights.parsers.ssl_certificate.CertificateChain` for more
        details.

    Sample Output::

        subject= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=test.a.com
        notAfter=Jan 18 07:02:33 2038 GMT

        subject= /C=US/ST=North Carolina/O=Katello/OU=SomeOrgUnit/CN=test.b.com
        notAfter=Jan 18 07:02:43 2028 GMT

    Examples:
        >>> type(satellite_ca_certs)
        <class 'insights.parsers.ssl_certificate.SatelliteCustomCaChain'>
        >>> len(satellite_ca_certs)
        2
        >>> satellite_ca_certs.earliest_expiry_date.str
        'Jan 18 07:02:43 2028'
    """
    pass


@parser(Specs.rhsm_katello_default_ca_cert)
class RhsmKatelloDefaultCACert(CertificateInfo):
    """
    .. note::
        Please refer to its super-class :class:`insights.parsers.ssl_certificate.CertificateInfo` for more
        details.

    Sample Output::

        issuer= /C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com

    Examples:
        >>> type(rhsm_katello_default_ca)
        <class 'insights.parsers.ssl_certificate.RhsmKatelloDefaultCACert'>
        >>> rhsm_katello_default_ca['issuer']
        '/C=US/ST=North Carolina/L=Raleigh/O=Katello/OU=SomeOrgUnit/CN=a.b.c.com'
    """
    pass
