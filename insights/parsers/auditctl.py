"""
AuditCtl - command ``auditctl xxx``
===================================

This module contains the following parsers:

AuditRules - command ``auditctl -l``
------------------------------------
AuditStatus - command ``auditctl -s``
-------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.auditctl_rules)
class AuditRules(CommandParser, list):
    """
    Class for parsing the `auditctl -l` command.
    All lines are stored in a list.

    Typical output of the command is::

        -w /etc/selinux -p wa -k MAC-policy
        -a always,exit -F arch=b32 -S chmod -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b64 -S chmod -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b32 -S chmod -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b64 -S chmod -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b32 -S chown -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b64 -S chown -F exit=-EACCES -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b32 -S chown -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access
        -a always,exit -F arch=b64 -S chown -F exit=-EPERM -F auid>=1000 -F auid!=-1 -F key=access

    Examples:
        >>> type(audit_rules)
        <class 'insights.parsers.auditctl.AuditRules'>
        >>> len(audit_rules)
        9
        >>> '-w /etc/selinux -p wa -k MAC-policy' in audit_rules
        True

    Raises:
        SkipComponent: When there are not rules.
    """

    def parse_content(self, content):
        if len(content) == 1 and content[0].lower().strip() == 'no rules':
            raise SkipComponent
        for line in content:
            if line.strip():
                self.append(line.strip())
        if not self:
            raise SkipComponent('No rules found')


@parser(Specs.auditctl_status)
class AuditStatus(CommandParser, dict):
    """
    Module for parsing the output of the ``auditctl -s`` command.

    Typical output on RHEL6 looks like::

        AUDIT_STATUS: enabled=1 flag=1 pid=1483 rate_limit=0 backlog_limit=8192 lost=3 backlog=0

    , while on RHEL7 and later, the output changes to::

        enabled 1
        failure 1
        pid 947
        rate_limit 0
        backlog_limit 320
        lost 0
        backlog 0
        loginuid_immutable 0 unlocked

    Example:
        >>> type(auds)
        <class 'insights.parsers.auditctl.AuditStatus'>
        >>> "enabled" in auds
        True
        >>> auds['enabled']
        1
    """
    def parse_content(self, content):
        if not content:
            raise SkipComponent("Input content is empty.")
        if len(content) > 1:
            for line in content:
                k, v = line.split(None, 1)
                # Mind the 'loginuid_immutable' on RHEL7
                if k.strip() == "loginuid_immutable":
                    self[k.strip()] = v.strip()
                else:
                    try:
                        self[k.strip()] = int(v.strip())
                    except ValueError:
                        raise ParseException('Unexpected type in line %s' % line)
        if len(content) == 1:
            line = list(content)[0].strip()
            if line.startswith("AUDIT_STATUS:"):
                for item in line.split(None)[1:]:
                    try:
                        k, v = item.split('=')
                        self[k.strip()] = int(v.strip())
                    except ValueError:
                        raise ParseException('Unexpected type in line %s ' % line)
        if not self:
            raise SkipComponent('There is no content in the status output.')
