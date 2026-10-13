"""
Sysroles Fingerprint - file ``/var/log/sysroles.jsonl``
========================================================

This module provides a parser for the RHEL System Roles fingerprint data
stored in ``/var/log/sysroles.jsonl``. The file is in JSONL (newline-delimited JSON)
format, where each line contains a separate JSON object representing a system role
execution fingerprint.
"""

import json

from insights.core import Parser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sysroles_fingerprint)
class SysrolesFingerprint(Parser, list):
    """
    Parse the ``/var/log/sysroles.jsonl`` file containing RHEL System Roles
    fingerprint data in JSONL format.

    The parser reads each line as a separate JSON object and stores them in a list.
    Each record represents an execution fingerprint from the rhel-system-roles package.

    Sample input::

        {"date": "2026-08-03T10:15:00+02:00", "role_name": "redhat.rhel_system_roles.network", "role_path": "/usr/share/ansible/roles/linux-system-roles.network", "status": "success", "ansible_version": "2.16.3", "managed_node_distro": "RedHat-9.4", "play_hosts_number": 3, "ansible_check_mode": false}
        {"date": "2026-08-03T10:18:22+02:00", "role_name": "redhat.rhel_system_roles.timesync", "role_path": "/usr/share/ansible/roles/linux-system-roles.timesync", "status": "success", "ansible_version": "2.16.3", "managed_node_distro": "RedHat-9.4", "play_hosts_number": 3, "ansible_check_mode": false}

    Raises:
        SkipComponent: when the file is empty or contains no parsable data.
        ParseException: when any line contains invalid JSON.

    Examples:
        >>> type(sysroles_fingerprint)
        <class 'insights.parsers.sysroles_fingerprint.SysrolesFingerprint'>
        >>> len(sysroles_fingerprint)
        2
        >>> sysroles_fingerprint[0]['role_name']
        'redhat.rhel_system_roles.network'
        >>> sysroles_fingerprint[0]['status']
        'success'
        >>> sysroles_fingerprint[0]['play_hosts_number']
        3
        >>> sysroles_fingerprint[1]['role_name']
        'redhat.rhel_system_roles.timesync'
        >>> sysroles_fingerprint[1]['ansible_check_mode']
        False
    """

    def parse_content(self, content):
        if not content:
            raise SkipComponent("Empty output.")

        for line in content:
            line = line.strip()
            if line:
                try:
                    line_json = json.loads(line)
                except Exception:
                    raise ParseException("Invalid JSON line: {0}".format(line))

                if not isinstance(line_json, dict):
                    raise ParseException("Invalid JSON line: {0}".format(line))

                if line_json:
                    self.append(line_json)

        if len(self) == 0:
            raise SkipComponent("No parsable data found.")
