"""
AuditctlStatus - Report auditd status
=====================================
"""

from .. import parser, CommandParser, LegacyItemAccess
from ..parsers import ParseException
from ..specs import Specs


@parser(Specs.auditctl_status)
class AuditctlStatus(LegacyItemAccess, CommandParser):
    """
    Module for parsing the output of the ``auditctl -s`` command.

    Typical output on RHEL6 looks like::

        AUDIT_STATUS: enabled=1 flag=1 pid=1483 rate_limit=0 backlog_limit=8192 lost=3 backlog=0

    , while on RHEL7 the output changes to::

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
        <class 'insights.parsers.auditctl_status.AuditctlStatus'>
        >>> "enabled" in auds
        True
        >>> auds['enabled']
        1
    """
    def parse_content(self, content):
        if not content:
            raise ParseException("Input content is empty.")
        self.data = {}
        if len(content) > 1:
            for line in content:
                k, v = line.split(None, 1)
                # Mind the 'loginuid_immutable' on RHEL7
                if k.strip() == "loginuid_immutable":
                    self.data[k.strip()] = v.strip()
                else:
                    try:
                        self.data[k.strip()] = int(v.strip())
                    except ValueError:
                        continue
        if len(content) == 1:
            line = list(content)[0].strip()
            if line.startswith("AUDIT_STATUS:"):
                for item in line.split(None)[1:]:
                    try:
                        k, v = item.split('=')
                        self.data[k.strip()] = int(v.strip())
                    except ValueError:
                        continue
