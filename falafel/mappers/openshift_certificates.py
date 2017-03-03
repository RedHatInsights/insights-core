"""
openssl x509 -noout -enddate -in {crt} - Command
================================================

At the point of install/upgrade of a cluster, a number of SSL
certificates are created for internal operations which are likely
to have a short validity period.  This applies to ALL minor releases
of OpenShift v3

Examples:
    >>> openshift_certs = shared[OpenShiftCertificates]
    >>> openshift_certs.file_name
    'server.crt'
    >>> openshift_certs.GetExpirationDate()
    datetime.datetime(2018, 11, 25, 3, 2, 4)
"""

from .. import Mapper, mapper
import datetime


@mapper("openshift_certificates")
class OpenShiftCertificates(Mapper):
    "Class to parse the expiration date"
    def parse_content(self, content):
        """Parse the content of crt file"""
        self.data = content[0].split("=")[1].rsplit(" ", 1)[0]

    def GetExpirationDate(self):
        """datetime: return the expiration date in datetime format"""
        return datetime.datetime.strptime(self.data, '%b %d %H:%M:%S %Y')
