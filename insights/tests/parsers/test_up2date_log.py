from datetime import datetime
from insights.parsers.up2date_log import Up2dateLog
from insights.tests import context_wrap
import doctest
from insights.parsers import up2date_log

LOG1 = """
[Thu Feb  1 10:40:13 2018] rhn_register ERROR: can not find RHNS CA file: /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
[Thu Feb  1 10:40:22 2018] rhn_register ERROR: can not find RHNS CA file: /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
[Thu Feb  1 10:40:22 2018] rhn_register
Traceback (most recent call last):
  File "/usr/sbin/rhn_register", line 74, in <module>
    app.run()
  File "/usr/share/rhn/up2date_client/rhncli.py", line 96, in run
    sys.exit(self.main() or 0)
  File "/usr/sbin/rhn_register", line 60, in main
    if not up2dateAuth.getLoginInfo():
  File "/usr/share/rhn/up2date_client/up2dateAuth.py", line 228, in getLoginInfo
    login(timeout=timeout)
  File "/usr/share/rhn/up2date_client/up2dateAuth.py", line 179, in login
    server = rhnserver.RhnServer(timeout=timeout)
  File "/usr/share/rhn/up2date_client/rhnserver.py", line 172, in __init__
    timeout=timeout)
  File "/usr/share/rhn/up2date_client/rpcServer.py", line 172, in getServer
    raise up2dateErrors.SSLCertificateFileNotFound(msg)
<class 'up2date_client.up2dateErrors.SSLCertificateFileNotFound'>: ERROR: can not find RHNS CA file: /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT
""".strip()

LOG2 = """
[Thu Feb  1 02:46:25 2018] rhn_register updateLoginInfo() login info
[Thu Feb  1 02:46:35 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #1
[Thu Feb  1 02:46:40 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #2
[Thu Feb  1 02:46:45 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #3
[Thu Feb  1 02:46:50 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #4
[Thu Feb  1 02:46:55 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #5
"""


def test_up2date_log():
    ulog = Up2dateLog(context_wrap(LOG1))
    ern_list = ulog.get('ERROR')
    assert 3 == len(ern_list)
    assert ern_list[2]['raw_message'] == "<class 'up2date_client.up2dateErrors.SSLCertificateFileNotFound'>: ERROR: can not find RHNS CA file: /usr/share/rhn/RHN-ORG-TRUSTED-SSL-CERT"
    assert len(list(ulog.get_after(datetime(2018, 2, 1, 10, 40, 22)))) == 18

    ulog = Up2dateLog(context_wrap(LOG2))
    ern_list = ulog.get('Temporary failure in name resolution')
    assert 5 == len(ern_list)
    assert ern_list[0]['raw_message'] == "[Thu Feb  1 02:46:35 2018] rhn_register A socket error occurred: (-3, 'Temporary failure in name resolution'), attempt #1"
    assert len(list(ulog.get_after(datetime(2018, 2, 1, 2, 46, 45)))) == 3


def test_up2date_log_doc_examples():
    env = {
        'Up2dateLog': Up2dateLog,
        'ulog': Up2dateLog(context_wrap(LOG2)),
    }
    failed, total = doctest.testmod(up2date_log, globs=env)
    assert failed == 0
