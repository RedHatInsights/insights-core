import pytest
from insights.parsers.audit_log import AuditLog
from insights.tests import context_wrap
from datetime import date

AUDIT_LOG_TEMPALTE = """
type=CRYPTO_KEY_USER msg=audit(1506046832.641:53584): pid=16865 uid=0 auid=0 ses=7247 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=destroy kind=session fp=? direction=both spid=16865 suid=0 rport=59296 laddr=192.0.2.1 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.66.136.139 terminal=? res=success'
type=LOGIN msg=audit(1506047401.407:53591): pid=482 uid=0 subj=system_u:system_r:crond_t:s0-s0:c0.c1023 old-auid=4294967295 auid=993 old-ses=4294967295 ses=7389 res=1
%s
type=CRED_REFR msg=audit(1508476956.471:13339): pid=30909 uid=0 auid=0 ses=1559 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=PAM:setcred grantors=pam_unix acct="root" exe="/usr/sbin/sshd" hostname=foo.example.com addr=192.0.2.2 terminal=ssh res=success'
""".strip()

AUDIT_LOG_NORMAL = """
type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket
""".strip()

AUDIT_LOG_START_WITH_SOME_WIRED_STRINGS = """
START WITH SOME WIRED STRINGS type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket
""".strip()

AUDIT_LOG_WITHOUT_TIMESTAMP_FIELD = """
type=AVC msg=audit: avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket
""".strip()

AUDIT_LOG_WITH_INVALID_TIMESTAMP_FIELD = """
type=AVC msg=audit(1506487181.009): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket
""".strip()

AUDIT_LOG_WITH_JUST_HEAD_PART = """
type=AVC msg=audit(1506487181.009:32794):
""".strip()

AUDIT_LOG_WITHOUT_JUST_TAIL_PART = """
type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for
""".strip()

DUMMY_AUDIT_LOG_1 = """
type=AVC
""".strip()

DUMMY_AUDIT_LOG_2 = """
type=AVC msg=whatever(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket
""".strip()

DUMMY_AUDIT_LOG_3 = """
type=AVC msg=audit(1506abc181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket
""".strip()

LAST_LINE_OF_TEMPLATE = """type=CRED_REFR msg=audit(1508476956.471:13339): pid=30909 uid=0 auid=0 ses=1559 subj=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023 msg='op=PAM:setcred grantors=pam_unix acct="root" exe="/usr/sbin/sshd" hostname=foo.example.com addr=192.0.2.2 terminal=ssh res=success'"""


def test_audit_log():

    auditlog = AuditLog(context_wrap(AUDIT_LOG_TEMPALTE % AUDIT_LOG_NORMAL))

    info = auditlog.get(['type=', 'msg='])
    assert len(info) == 4
    info = auditlog.get('type=')
    assert len(info) == 4
    line0 = info[0]
    assert line0.get('type') == 'CRYPTO_KEY_USER'
    assert line0.get('msg') == 'op=destroy kind=session fp=? direction=both spid=16865 suid=0 rport=59296 laddr=192.0.2.1 lport=22  exe="/usr/sbin/sshd" hostname=? addr=10.66.136.139 terminal=? res=success'
    assert line0.get('unparsed') is None
    line2 = info[2]
    assert line2.get('unparsed') == 'avc:  denied  { create } for'
    assert line2.get('comm') == 'mongod'
    assert line2.get('raw_message') == 'type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for  pid=27960 comm="mongod" scontext=system_u:system_r:mongod_t:s0 tcontext=system_u:system_r:mongod_t:s0 tclass=unix_dgram_socket'

    logtime = date.fromtimestamp(1506047401.407)
    logs = list(auditlog.get_after(timestamp=logtime))
    assert logs[0] == {'timestamp': '1506487181.009', 'is_valid': True,
            'unparsed': 'avc:  denied  { create } for',
            'msg_ID': '32794', 'pid': '27960', 'raw_message': AUDIT_LOG_NORMAL,
            'comm': 'mongod', 'scontext': 'system_u:system_r:mongod_t:s0',
            'tclass': 'unix_dgram_socket', 'type': 'AVC',
            'tcontext': 'system_u:system_r:mongod_t:s0'}
    assert logs[1]['raw_message'] == LAST_LINE_OF_TEMPLATE

    logs = list(auditlog.get_after(timestamp=logtime, s='AVC'))
    assert len(logs) == 1
    logs = list(auditlog.get_after(timestamp=logtime, s=['type=', 'AVC']))
    assert len(logs) == 1
    logs = list(auditlog.get_after(timestamp=logtime, s='NOTEXIST'))
    assert len(logs) == 0
    with pytest.raises(TypeError):
        list(auditlog.get_after(timestamp=logtime, s=['type=', False, 'AVC']))
    with pytest.raises(TypeError):
        list(auditlog.get_after(timestamp=logtime, s=set(['type=', 'AVC'])))

    options = [AUDIT_LOG_START_WITH_SOME_WIRED_STRINGS,
               AUDIT_LOG_WITH_INVALID_TIMESTAMP_FIELD,
               AUDIT_LOG_WITH_INVALID_TIMESTAMP_FIELD,
               DUMMY_AUDIT_LOG_1, DUMMY_AUDIT_LOG_2]

    for option in options:
        auditlog = AuditLog(context_wrap(AUDIT_LOG_TEMPALTE % option))
        info = auditlog.get('type=')
        assert len(info) == 4
        assert info[2].get('is_valid') is False
        assert info[3].get('type') == 'CRED_REFR'

        logtime = date.fromtimestamp(1506047401.407)
        logs = list(auditlog.get_after(timestamp=logtime))
        assert logs[0]['raw_message'] == LAST_LINE_OF_TEMPLATE

    auditlog = AuditLog(context_wrap(AUDIT_LOG_TEMPALTE % AUDIT_LOG_WITH_JUST_HEAD_PART))
    info = auditlog.get("type=AVC")
    assert len(info) == 1
    line0 = info[0]
    assert line0.get('unparsed') is None
    assert line0 == {'timestamp': '1506487181.009', 'msg_ID': '32794',
                     'is_valid': True, 'type': 'AVC',
                     'raw_message': 'type=AVC msg=audit(1506487181.009:32794):'}

    auditlog = AuditLog(context_wrap(AUDIT_LOG_TEMPALTE % AUDIT_LOG_WITHOUT_JUST_TAIL_PART))
    info = auditlog.get('type=')
    assert len(info) == 4
    line2 = info[2]
    assert line2.get('is_valid') is True
    assert line2.get('type') == 'AVC'
    assert line2.get('unparsed') == 'avc:  denied  { create } for'
    assert line2.get('raw_message') == 'type=AVC msg=audit(1506487181.009:32794): avc:  denied  { create } for'

    auditlog = AuditLog(context_wrap(AUDIT_LOG_TEMPALTE % DUMMY_AUDIT_LOG_3))
    info = auditlog.get('type=')
    assert len(info) == 4
    logtime = date.fromtimestamp(1506047401.407)
    logs = list(auditlog.get_after(timestamp=logtime))
    assert logs[0]['raw_message'] == LAST_LINE_OF_TEMPLATE
