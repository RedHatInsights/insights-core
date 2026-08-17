"""
SysrolesFingerprint - file ``/var/log/sysroles.jsonl``
=======================================================

Parser for the JSONL fingerprint log written by the ``sr_fingerprint``
Ansible module in RHEL System Roles. Each line is one JSON object
representing a single role execution.
"""
import json

from insights.core import Parser
from insights.core.exceptions import SkipComponent
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.sysroles_fingerprint)
class SysrolesFingerprint(Parser, list):
    """
    Parse the ``/var/log/sysroles.jsonl`` file written by the
    ``sr_fingerprint`` Ansible module in RHEL System Roles.

    The file is in JSONL format — one JSON object per line. Each record
    represents a single role execution.

    Attributes:
        list: Each element is a dict with the following keys:

            - **date** (str): ISO 8601 timestamp of the execution
            - **role_name** (str): Collection-qualified role name,
              e.g. ``redhat.rhel_system_roles.network``
            - **role_path** (str): Filesystem path to the role; indicates
              whether it was installed via RPM or Automation Hub
            - **status** (str): ``begin`` or ``success``
            - **ansible_version** (str): Ansible core version string
            - **managed_node_distro** (str): OS name and version of the
              managed node, e.g. ``RedHat-9.4``
            - **play_hosts_number** (int): Number of hosts in the play
            - **ansible_check_mode** (bool): ``True`` if run in check mode

    Raises:
        SkipComponent: When the file is empty or contains no valid records.

    Examples:
        >>> type(sysroles_fingerprint)
        <class 'insights.parsers.sysroles.SysrolesFingerprint'>
        >>> len(sysroles_fingerprint) > 0
        True
        >>> sysroles_fingerprint[0]['role_name']
        'redhat.rhel_system_roles.network'
        >>> sysroles_fingerprint[0]['status']
        'success'
        >>> sysroles_fingerprint[0]['play_hosts_number']
        3
    """
    def parse_content(self, content):
        records = []
        for line in content:
            line = line.strip()
            if line:
                records.append(json.loads(line))
        if not records:
            raise SkipComponent("No fingerprint records found")
        self.extend(records)
