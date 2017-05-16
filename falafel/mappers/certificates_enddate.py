"""
/usr/bin/openssl x509 -noout -enddate -in path/to/cert/file - Command
=====================================================================

This command gets the enddates of certificate files.

Typical output of this command is::

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
    >>> cert_enddate = shared[CertificatesEnddate]
    >>> paths = cert_enddate.get_certificates_path
    >>> paths[0]
    /etc/origin/node/cert.pem
    >>> cert_enddate.get_expiration_date(paths[0])
    datetime(2019, 05, 25, 16, 39, 40)
"""

from datetime import datetime
from .. import Mapper, mapper


@mapper("certificates_enddate")
class CertificatesEnddate(Mapper):
    "Class to parse the expiration dates"

    def parse_content(self, content):
        """Parse the content of crt files"""
        self.data = {}
        datestamp = None
        for l in content:
            if datestamp and l.startswith("FileName="):
                self.data[l.split("=")[-1].strip()] = datestamp
                datestamp = None
            elif l.startswith("notAfter="):
                datestamp = l.split("=")[-1].rsplit(" ", 1)[0]
            else:
                datestamp = None

    @property
    def certificates_path(self):
        """return filepaths in list"""
        return self.data.keys() if self.data else []

    def get_expiration_date(self, path):
        """datetime: return the expiration date in datetime format"""
        try:
            return (datetime.strptime(self.data[path], '%b %d %H:%M:%S %Y')
                    if self.data and path in self.data else None)
        except:
            raise Exception("Unable to parse the expiration data of %s" % path)
