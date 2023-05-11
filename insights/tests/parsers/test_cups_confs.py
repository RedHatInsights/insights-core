import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import cups_confs
from insights.parsers.cups_confs import CupsdConf, CupsFilesConf
from insights.parsr.query import first, last
from insights.tests import context_wrap

CUPSD_CONF = """
MaxLogSize 0
LogLevel warn

# Only listen for connections from the local machine.
Listen localhost:631
Listen /var/run/cups/cups.sock
Browsing On
BrowseLocalProtocols dnssd
DefaultAuthType Basic
WebInterface Yes
IdleExitTimeout 0

<Location />
  Order allow,deny
</Location>

<Location /admin>
  Order allow,deny
</Location>

<Location /admin/conf>
  AuthType Default
  Require user @SYSTEM
  Order allow,deny
</Location>

<Location /admin/log>
  AuthType Default
  Require user @SYSTEM
  Order allow,deny
</Location>

<Policy default>
  JobPrivateAccess default
  JobPrivateValues default
  SubscriptionPrivateAccess default
  SubscriptionPrivateValues default

  <Limit Create-Job Print-Job Print-URI Validate-Job>
    Order deny,allow
  </Limit>

  <Limit Pause-Printer Resume-Printer Enable-Printer Disable-Printer Pause-Printer-After-Current-Job Hold-New-Jobs Release-Held-New-Jobs Deactivate-Printer Activate-Printer Restart-Printer Shutdown-Printer Startup-Printer Promote-Job Schedule-Job-After Cancel-Jobs CUPS-Accept-Jobs CUPS-Reject-Jobs>
    AuthType Default
    Require user @SYSTEM
    Order deny,allow
  </Limit>

  <Limit Cancel-Job CUPS-Authenticate-Job>
    Require user @OWNER @SYSTEM
    Order deny,allow
  </Limit>

  <Limit All>
    Order deny,allow
  </Limit>
</Policy>
""".strip()

CUPSD_CONF_EXAMPLE = """
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
""".strip()

CUPSD_CONF_ERROR = """
</Limit>

<Limit All>
Order deny,allow
</Limit>
</Policy>
""".strip()

CUPS_FILES_CONF = """
FatalErrors config
SyncOnClose Yes
# Default user and group for filters/backends/helper programs; this cannot be
# any user or group that resolves to ID 0 for security reasons...
#User lp
#Group lp
# Administrator user group, used to match @SYSTEM in cupsd.conf policy rules...
# This cannot contain the Group value for security reasons...
SystemGroup sys root
SystemGroup wheel
# User that is substituted for unauthenticated (remote) root accesses...
#RemoteRoot remroot
AccessLog syslog
ErrorLog syslog
PageLog syslog
""".strip()

CUPS_FILES_CONF_EMPTY = """
""".strip()


def test_cupsd_conf():
    context = context_wrap(CUPSD_CONF)
    result = CupsdConf(context)
    assert result['Listen'][first].value == 'localhost:631'
    assert result['Listen'][last].value == '/var/run/cups/cups.sock'
    assert result[('Policy', 'default')][('Limit', 'Cancel-Job')]['Require'][first].value == "user @OWNER @SYSTEM"
    assert result[('Policy', 'default')][('Limit', 'CUPS-Authenticate-Job')]['Require'][first].value == "user @OWNER @SYSTEM"
    assert result[('Location', '/admin')]['Order'][last].value == 'allow,deny'


def test_cupsd_conf_error():
    with pytest.raises(ParseException) as exc:
        CupsdConf(context_wrap(CUPSD_CONF_ERROR))
    assert str(exc.value) == "There was an exception when parsing the cupsd.conf file"


def test_cups_files_conf():
    result = CupsFilesConf(context_wrap(CUPS_FILES_CONF))
    assert len(result) == 6
    assert 'SyncOnClose' in result
    assert result['SystemGroup'] == ['sys', 'root', 'wheel']
    assert result['AccessLog'] == 'syslog'


def test_cups_files_conf_empyt():
    with pytest.raises(ParseException) as exc:
        CupsFilesConf(context_wrap(CUPS_FILES_CONF_EMPTY))
    assert str(exc.value) == "Empty Content"


def test_doc():
    env = {
        'cupsd_conf': CupsdConf(context_wrap(CUPSD_CONF_EXAMPLE)),
        'cups_files_conf': CupsFilesConf(context_wrap(CUPS_FILES_CONF))
    }
    failed, total = doctest.testmod(cups_confs, globs=env)
    assert failed == 0
