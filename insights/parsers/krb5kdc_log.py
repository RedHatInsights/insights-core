"""
Kerberos KDC Logs - file ``/var/log/krb5kdc.log``
=================================================

"""

from .. import LogFileOutput, parser

import re
from insights.specs import kerberos_kdc_log


@parser(kerberos_kdc_log)
class KerberosKDCLog(LogFileOutput):
    '''
    Read the ``/var/log/krb5kdc.log`` file.  For more usage information see
    the ``LogFileOutput`` parser class.

    Sample log file::

        Apr 01 03:36:11 ldap.example.com krb5kdc[24569](info): TGS_REQ (4 etypes {18 17 16 23}) 10.250.3.150: ISSUE: authtime 1427873771, etypes {rep=18 tkt=18 ses=18}, sasher@EXAMPLE.COM for HTTP/sepdt138.example.com@EXAMPLE.COM
        Apr 01 03:36:11 ldap.example.com krb5kdc[24569](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.17.96: NEEDED_PREAUTH: niz@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
        Apr 01 03:36:11 ldap.example.com krb5kdc[24549](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.17.96: NEEDED_PREAUTH: niz@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
        Apr 01 03:36:11 ldap.example.com krb5kdc[24546](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.17.96: NEEDED_PREAUTH: niz@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
        Apr 01 03:36:33 ldap.example.com krb5kdc[24556](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed
        Apr 01 03:36:36 ldap.example.com krb5kdc[24568](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
        Apr 01 03:38:34 ldap.example.com krb5kdc[24551](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
        Apr 01 03:39:43 ldap.example.com krb5kdc[24549](info): preauth (encrypted_timestamp) verify failure: No matching key in entry

    Examples:
        >>> log = shared[KerberosKDCLog]
        >>> # log.get is a generator, so get list to test length
        >>> len(list(log.get('Decrypt integrity check failed')))
        1
        >>> from datetime import datetime
        >>> len(log.get_after(datetime(2017, 4, 1, 3, 36, 30)))  # Apr 01 03:36:30
        4

    Note:
        Because the Kerberos KDC log timestamps by default have no year,
        the year of the logs will be inferred from the year in your timestamp.
        This will also work around December/January crossovers.
    '''
    time_format = '%b %d %H:%M:%S'

    def get(self, keyword):
        '''
        Find logs by keyword and parse them into a dictionary with the keys:

        * `timestamp`
        * `system`
        * `service`
        * `pid`
        * `level`
        * `message`
        * `line` - the full line as originally given.

        If the log line is not in the standard format, only the 'line' field
        will be stored in the dictionary.

        Parameters:
            keyword(str): a keyword to search for in the line

        Yields:
            (dict): A dictionary for each parsed line in the input.
        '''
        line_re = re.compile(
            r'(?P<timestamp>\w{3} \d\d \d\d:\d\d:\d\d) ' +
            r'(?P<system>\w\S+) ' +
            r'(?P<service>\w+)\[(?P<pid>\d+)\]\((?P<level>\w+)\): ' +
            r'(?P<message>.*)'
        )
        for line in self.lines:
            if keyword in line:
                data = {
                    'line': line
                }
                match = line_re.search(line)
                if match:
                    data.update(match.groupdict())
                yield data
