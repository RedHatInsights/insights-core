"""
CertificatesEnddate - command ``/usr/bin/openssl x509 -noout -enddate -in path/to/cert/file``
=============================================================================================

This command gets the enddate of the certificate files.

Sample Output::

    /usr/bin/find: '/etc/origin/node': No such file or directory
    /usr/bin/find: '/etc/origin/master': No such file or directory
    notAfter=May 25 16:39:40 2019 GMT
    FileName= /etc/origin/node/cert.pem
    unable to load certificate
    139881193203616:error:0906D066:PEM routines:PEM_read_bio:bad end line:pem_lib.c:802:
    unable to load certificate
    140695459370912:error:0906D06C:PEM routines:PEM_read_bio:no start line:pem_lib.c:703:Expecting: TRUSTED CERTIFICATE
    notAfter=May 25 16:39:40 2019 GMT
    FileName= /etc/pki/ca-trust/extracted/pem/email-ca-bundle.pem
    notAfter=Dec  9 10:55:38 2017 GMT
    FileName= /etc/pki/consumer/cert.pem
    notAfter=Jan  1 04:59:59 2022 GMT
    FileName= /etc/pki/entitlement/3343502840335059594.pem
    notAfter=Aug 31 02:19:59 2017 GMT
    FileName= /etc/pki/consumer/cert.pem
    notAfter=Jan  1 04:59:59 2022 GMT
    FileName= /etc/pki/entitlement/2387590574974617178.pem

Examples:
    >>> type(cert_enddate)
    <class 'insights.parsers.certificates_enddate.CertificatesEnddate'>
    >>> paths = cert_enddate.certificates_path
    >>> '/etc/origin/node/cert.pem' in paths
    True
    >>> cert_enddate.expiration_date('/etc/origin/node/cert.pem').datetime
    datetime.datetime(2019, 5, 25, 16, 39, 40)
    >>> cert_enddate.expiration_date('/etc/origin/node/cert.pem').str
    'May 25 16:39:40 2019'
"""
from collections import namedtuple
from datetime import datetime

from insights.core import CommandParser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.certificates_enddate)
class CertificatesEnddate(CommandParser, dict):
    """Class to parse the expiration date."""

    ExpirationDate = namedtuple('ExpirationDate', ['str', 'datetime'])
    """namedtuple: contains the expiration date in string and datetime format."""

    def parse_content(self, content):
        """Parse the content of crt files."""
        datestamp = None
        for l in content:
            if datestamp and l.startswith("FileName="):
                self[l.split("=")[-1].strip()] = datestamp
                datestamp = None
            elif l.startswith("notAfter="):
                datestamp = l.split("=")[-1].rsplit(" ", 1)[0]
            else:
                datestamp = None
        if not self:
            raise SkipComponent("No certification files found.")

    @property
    def data(self):
        """ Set data as property to keep compatibility """
        return self

    @property
    def certificates_path(self):
        """list: Return filepaths in list or []."""
        return self.data.keys() if self.data else []

    def expiration_date(self, path):
        """This will return a namedtuple(['str', 'datetime']) contains the
        expiration date in string and datetime format. If the expiration date
        is unparsable, the ExpirationDate.datetime should be None.

        Args:
            path(str): The certificate file path.

        Returns:
            A ExpirationDate for available path. None otherwise.
        """
        path_date = self.data.get(path)
        if path_date:
            try:
                path_datetime = datetime.strptime(path_date, '%b %d %H:%M:%S %Y')
                return self.ExpirationDate(path_date, path_datetime)
            except Exception:
                return self.ExpirationDate(path_date, None)
