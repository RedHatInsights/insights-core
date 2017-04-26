"""
openssl x509 -noout -enddate -in {crt} - Command
================================================

This command gets the enddates of certificate files.
The value 'crt' is the output of the pre_command
"/usr/bin/find /etc/origin/node /etc/origin/master /etc/pki -type f".

Examples:
    >>> cert_enddate = shared[CertificatesEnddate]
    >>> cert_enddate.file_name
    'server.crt'
    >>> cert_enddate.get_expiration_date()
    datetime.datetime(2018, 11, 25, 3, 2, 4)
"""

import datetime
from .. import Mapper, mapper


@mapper("certificates_enddate")
class CertificatesEnddate(Mapper):
    "Class to parse the expiration date"

    def parse_content(self, content):
        """Parse the content of crt file"""
        self.data = (content[0].split("=")[-1].rsplit(" ", 1)[0]
                     if (len(content) == 1 and "=" in content[0])
                     else None)

    def get_expiration_date(self):
        """datetime: return the expiration date in datetime format"""
        try:
            return (datetime.datetime.strptime(self.data, '%b %d %H:%M:%S %Y')
                    if self.data else None)
        except:
            raise Exception("Unable to parse the expiration data of %s" %
                            self.file_path)
