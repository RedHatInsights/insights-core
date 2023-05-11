"""
CUPS configuration files
========================

Parsers provided by this module are:

CupsdConf - file ``/etc/cups/cupsd.conf``
-----------------------------------------
CupsFilesConf - file ``/etc/cups/cups-files.conf``
--------------------------------------------------
"""

from insights.core import Parser, ConfigParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.parsers import get_active_lines
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


@parser(Specs.cups_files_conf)
class CupsFilesConf(Parser, dict):
    """
    Class for parsing the file ``/etc/cups/cups-files.conf``

    Sample file content::

        FatalErrors config
        SyncOnClose Yes
        SystemGroup sys root wheel
        AccessLog syslog
        ErrorLog syslog
        PageLog syslog

    Examples:
        >>> type(cups_files_conf)
        <class 'insights.parsers.cups_confs.CupsFilesConf'>
        >>> cups_files_conf['FatalErrors']
        'config'
        >>> cups_files_conf['SyncOnClose']
        'Yes'
        >>> 'wheel' in cups_files_conf['SystemGroup']
        True
    """

    def parse_content(self, content):
        if not content:
            raise ParseException('Empty Content')

        for line in get_active_lines(content):
            k, v = [i.strip() for i in line.split(None, 1)]
            if k not in self:
                self[k] = v if len(v.split()) == 1 else v.split()
            else:
                _v = self[k]
                _v = [_v] if not isinstance(_v, list) else _v
                if v not in _v:
                    _v.append(v)
                    self[k] = _v
