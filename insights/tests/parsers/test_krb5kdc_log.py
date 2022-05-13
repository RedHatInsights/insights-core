from insights.parsers.krb5kdc_log import KerberosKDCLog
from insights.tests import context_wrap

from datetime import datetime

KRB5KDC_LOG = """
Apr 01 03:36:01 ldap.example.com krb5kdc[24554](info): TGS_REQ (7 etypes {18 17 23 3 1 24 -135}) 10.250.2.47: UNKNOWN_SERVER: authtime 0,  opshzl@EXAMPLE.COM for cifs/secifs1.example.com@EXAMPLE.COM, Server not found in Kerberos database
Apr 01 03:36:04 ldap.example.com krb5kdc[24554](info): TGS_REQ (7 etypes {18 17 23 3 1 24 -135}) 10.250.18.199: UNKNOWN_SERVER: authtime 0,  pdtsro@EXAMPLE.COM for cifs/nyqrm4.example.com@EXAMPLE.COM, Server not found in Kerberos database
Apr 01 03:36:11 ldap.example.com krb5kdc[24554](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.3.150: NEEDED_PREAUTH: sasher@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
Apr 01 03:36:11 ldap.example.com krb5kdc[24570](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.3.150: ISSUE: authtime 1427873771, etypes {rep=18 tkt=18 ses=18}, sasher@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM
Apr 01 03:36:11 ldap.example.com krb5kdc[24569](info): TGS_REQ (4 etypes {18 17 16 23}) 10.250.3.150: ISSUE: authtime 1427873771, etypes {rep=18 tkt=18 ses=18}, sasher@EXAMPLE.COM for HTTP/sepdt138.example.com@EXAMPLE.COM
Apr 01 03:36:11 ldap.example.com krb5kdc[24569](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.17.96: NEEDED_PREAUTH: niz@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
Apr 01 03:36:11 ldap.example.com krb5kdc[24549](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.17.96: NEEDED_PREAUTH: niz@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
Apr 01 03:36:11 ldap.example.com krb5kdc[24546](info): AS_REQ (4 etypes {18 17 16 23}) 10.250.17.96: NEEDED_PREAUTH: niz@EXAMPLE.COM for krbtgt/EXAMPLE.COM@EXAMPLE.COM, Additional pre-authentication required
Apr 01 03:36:33 ldap.example.com krb5kdc[24556](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed
Apr 01 03:36:36 ldap.example.com krb5kdc[24568](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:38:34 ldap.example.com krb5kdc[24551](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:39:43 ldap.example.com krb5kdc[24549](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:39:43 ldap.example.com krb5kdc[24557](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:40:01 ldap.example.com krb5kdc[24570](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:40:15 ldap.example.com krb5kdc[24557](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed
Apr 01 03:40:18 ldap.example.com krb5kdc[24560](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed
Apr 01 03:40:20 ldap.example.com krb5kdc[24555](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:40:21 ldap.example.com krb5kdc[24560](info): preauth (encrypted_timestamp) verify failure: No matching key in entry
Apr 01 03:40:42 ldap.example.com krb5kdc[24573](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed
Apr 01 03:40:42 ldap.example.com krb5kdc[24568](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed
krb5kdc: setsockopt(7,IPV6_V6ONLY,1) worked
"""


def test_krb5kdc_log():
    log = KerberosKDCLog(context_wrap(KRB5KDC_LOG))
    assert len(log.lines) == 21
    decrypt_failed_logs = log.get('Decrypt integrity check failed')
    assert len(decrypt_failed_logs) == 5
    assert decrypt_failed_logs[0] == {
        'raw_message': 'Apr 01 03:36:33 ldap.example.com krb5kdc[24556](info): preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed',
        'timestamp': 'Apr 01 03:36:33',
        'system': 'ldap.example.com',
        'service': 'krb5kdc',
        'pid': '24556',
        'level': 'info',
        'message': 'preauth (encrypted_timestamp) verify failure: Decrypt integrity check failed'
    }
    # Lines that don't parse still get found and just have the 'line' key
    assert len(list(log.get('setsockopt'))) == 1
    assert log.get('setsockopt')[0] == {
        'raw_message': 'krb5kdc: setsockopt(7,IPV6_V6ONLY,1) worked'
    }

    # test get_after, including continuation line
    assert len(list(log.get_after(datetime(2016, 4, 1, 3, 40, 0)))) == 8
