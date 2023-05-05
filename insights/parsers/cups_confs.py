"""
CUPS configuration files
========================

Parsers provided by this module are:

CupsdConf - file ``/etc/cups/cupsd.conf``
-----------------------------------------
"""

from insights.core import ConfigParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers.httpd_conf import DocParser
from insights.core.exceptions import ParseException
from insights.parsr.query import Entry


class CupsdConfBase(DocParser):

    def __call__(self, content):
        try:
            return self.Top(content)
        except Exception:
            raise ParseException("There was an exception when parsing the cupsd.conf file")


@parser(Specs.cupsd_conf)
class CupsdConf(ConfigParser):
    """
    Class for parsing the file ``/etc/cups/cupsd.conf``

    Sample file content::

        MaxLogSize 0
        LogLevel warn
        Listen localhost:631
        Listen /var/run/cups/cups.sock
        Browsing On
        BrowseLocalProtocols dnssd

        <Location />
          Order allow,deny
        </Location>

        <Policy default>
          JobPrivateAccess default
          JobPrivateValues default
          SubscriptionPrivateAccess default
          SubscriptionPrivateValues default

          <Limit Send-Document Send-URI Hold-Job Release-Job Restart-Job Purge-Jobs Set-Job-Attributes Create-Job-Subscription Renew-Subscription Cancel-Subscription Get-Notifications Reprocess-Job Cancel-Current-Job Suspend-Current-Job Resume-Job Cancel-My-Jobs Close-Job CUPS-Move-Job CUPS-Get-Document>
            Require user @OWNER @SYSTEM
            Order deny,allow
          </Limit>

          <Limit All>
            Order deny,allow
          </Limit>
        </Policy>

    Examples:
        >>> type(cupsd_conf)
        <class 'insights.parsers.cups_confs.CupsdConf'>
        >>> cupsd_conf['MaxLogSize'][-1].value
        0
        >>> cupsd_conf['Listen'][0].value
        'localhost:631'
        >>> cupsd_conf['Listen'][-1].value
        '/var/run/cups/cups.sock'
        >>> cupsd_conf[('Location', '/')]['Order'][-1].value
        'allow,deny'
        >>> cupsd_conf[('Policy','default')][('Limit','Send-Document')]['Order'][0].value
        'deny,allow'
        >>> 'JobPrivateAccess' in cupsd_conf[('Policy','default')]
        True
    """

    def __init__(self, *args, **kwargs):
        self.parse = CupsdConfBase(self)
        super(CupsdConf, self).__init__(*args, **kwargs)

    def parse_doc(self, content):
        if isinstance(content, list):
            content = "\n".join(content)
        result = self.parse(content)[0]
        return Entry(children=result, src=self)
