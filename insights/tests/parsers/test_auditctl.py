import doctest
import pytest

from insights.core.exceptions import ParseException, SkipComponent
from insights.parsers import auditctl
from insights.parsers.auditctl import AuditStatus, AuditRules
from insights.tests import context_wrap

NORMAL_AUDS_RHEL6 = """
AUDIT_STATUS: enabled=1 flag=1 pid=1483 rate_limit=0 backlog_limit=8192 lost=3 backlog=0
""".strip()

BAD_AUDS_RHEL6 = """
AUDIT_STATUS: enabled=1 flag=1 pid=1483 rate_limit=0 backlog_limit=8192 lost=3 backlog=0 test=test
""".strip()

NORMAL_AUDS_RHEL7 = """
enabled 1
failure 1
pid 947
rate_limit 0
backlog_limit 320
lost 0
backlog 0
loginuid_immutable 1 locked
""".strip()

BAD_AUDS_RHEL7 = """
enabled 1
failure 1
pid 947
rate_limit 0
backlog_limit 320
lost 0
backlog 0
test test
loginuid_immutable 1 locked
""".strip()

BLANK_INPUT_SAMPLE = """
""".strip()

BAD_INPUT_SAMPLE = """
Unknown: type=0, len=0
""".strip()

BAD_INPUT_MIX = """
Unknown: type=0, len=0
enabled 1
""".strip()

AUDIT_RULES_OUTPUT1 = """
No rules
""".strip()

AUDIT_RULES_OUTPUT2 = """
-w /etc/selinux -p wa -k MAC-policy
-a always,exit -F arch=b32 -S chmod -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b64 -S chmod -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b32 -S chmod -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b64 -S chmod -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access

-a always,exit -F arch=b32 -S chown -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b64 -S chown -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b32 -S chown -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
-a always,exit -F arch=b64 -S chown -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
""".strip()

AUDIT_RULES_OUTPUT3 = """

"""


def test_normal_auds_rhel6():
    auds = AuditStatus(context_wrap(NORMAL_AUDS_RHEL6))
    assert "enabled" in auds
    assert "loginuid_immutable" not in auds
    assert auds['pid'] == 1483


def test_normal_auds_rhel7():
    auds = AuditStatus(context_wrap(NORMAL_AUDS_RHEL7))
    assert "loginuid_immutable" in auds
    assert auds['loginuid_immutable'] == "1 locked"
    assert auds['failure'] == 1
    assert auds.get('nonexists') is None


def test_auds_blank_input():
    ctx = context_wrap(BLANK_INPUT_SAMPLE)
    with pytest.raises(SkipComponent) as sc:
        AuditStatus(ctx)
    assert "Input content is empty." in str(sc)
    with pytest.raises(SkipComponent):
        AuditStatus(context_wrap(BAD_INPUT_SAMPLE))


def test_parse_exception():
    with pytest.raises(ParseException):
        AuditStatus(context_wrap(BAD_AUDS_RHEL7))
    with pytest.raises(ParseException):
        AuditStatus(context_wrap(BAD_AUDS_RHEL6))


def test_audit_rules():
    audit_rules = AuditRules(context_wrap(AUDIT_RULES_OUTPUT2))
    assert len(audit_rules) == 9
    assert '-w /etc/selinux -p wa -k MAC-policy' in audit_rules


def test_audit_rules_exception():
    with pytest.raises(SkipComponent):
        AuditRules(context_wrap(AUDIT_RULES_OUTPUT1))
    with pytest.raises(SkipComponent):
        AuditRules(context_wrap(AUDIT_RULES_OUTPUT3))


def test_doc_examples():
    env = {
        'audit_rules': AuditRules(context_wrap(AUDIT_RULES_OUTPUT2)),
        'auds': AuditStatus(context_wrap(NORMAL_AUDS_RHEL7))
    }
    failed, total = doctest.testmod(auditctl, globs=env)
    assert failed == 0
