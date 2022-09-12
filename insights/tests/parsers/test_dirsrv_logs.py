from insights.parsers.dirsrv_logs import DirSrvAccessLog, DirSrvErrorsLog
from insights.tests import context_wrap

import datetime

ACCESS_LOG = '''
    389-Directory/1.2.11.15 B2014.300.2010
    ldap.example.com:636 (/etc/dirsrv/slapd-EXAMPLE-COM)

[27/Apr/2015:13:16:35 -0400] conn=1174478 fd=131 slot=131 connection from 10.20.10.106 to 10.20.62.16
[27/Apr/2015:13:16:35 -0400] conn=1174478 op=-1 fd=131 closed - B1
[27/Apr/2015:13:16:35 -0400] conn=324375 op=606903 SRCH base="cn=users,cn=accounts,dc=example,dc=com" scope=2 filter="(uid=root)" attrs=ALL
[27/Apr/2015:13:16:35 -0400] conn=324375 op=606903 RESULT err=0 tag=101 nentries=1 etime=0
[27/Apr/2015:13:16:35 -0400] conn=324375 op=606904 SRCH base="cn=groups,cn=accounts,dc=example,dc=com" scope=2 filter="(|(member=uid=root,cn=users,cn=accounts,dc=example,dc=com)(uniqueMember=uid=root,cn=users,cn=accounts,dc=example,dc=com)(memberUid=root))" attrs="cn"
[27/Apr/2015:13:16:35 -0400] conn=324375 op=606904 RESULT err=0 tag=101 nentries=8 etime=0
[27/Apr/2015:13:16:40 -0400] conn=1174483 fd=131 slot=131 connection from 10.20.130.21 to 10.20.62.16
[27/Apr/2015:13:16:40 -0400] conn=1174483 op=0 SRCH base="" scope=0 filter="(objectClass=*)" attrs="* altServer namingContexts aci"
[27/Apr/2015:13:16:40 -0400] conn=1174483 op=0 RESULT err=0 tag=101 nentries=1 etime=0
'''.strip()

ERRORS_LOG = '''
    389-Directory/1.2.11.15 B2014.300.2010
    ldap.example.com:7390 (/etc/dirsrv/slapd-PKI-IPA)

[23/Apr/2015:23:12:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
[23/Apr/2015:23:17:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
[23/Apr/2015:23:22:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
[23/Apr/2015:23:27:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
[23/Apr/2015:23:32:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
[23/Apr/2015:23:37:31 -0400] slapi_ldap_bind - Error: could not send startTLS request: error -11 (Connect error) errno 0 (Success)
'''


def test_access_log():
    # Note that this tests only one instance; it does not test iterating
    # through the logs as a normal rule would have to
    ctx = context_wrap(ACCESS_LOG, path='/var/log/dirsrv/slapd-EXAMPLE-COM/access')
    log = DirSrvAccessLog(ctx)
    assert log
    assert len(log.lines) == 12
    connects = log.get('connection from')
    assert len(connects) == 2
    assert '10.20.10.106' in connects[0]['raw_message']
    assert '10.20.130.21' in connects[1]['raw_message']
    tstamp = datetime.datetime(2015, 4, 27, 13, 16, 36)
    assert len(list(log.get_after(tstamp))) == 3
    assert len(list(log.get_after(tstamp, 'connection from'))) == 1


def test_error_log():
    # Note that this tests only one instance; it does not test iterating
    # through the logs as a normal rule would have to
    ctx = context_wrap(ERRORS_LOG, path='/var/log/dirsrv/slapd-PKI-IPA/errors')
    log = DirSrvErrorsLog(ctx)
    assert log
    assert len(log.lines) == 9
    connects = log.get('slapi_ldap_bind')
    assert len(connects) == 6
    assert 'could not send startTLS request' in connects[0]['raw_message']
    tstamp = datetime.datetime(2015, 4, 23, 23, 22, 31)
    assert len(list(log.get_after(tstamp))) == 4
