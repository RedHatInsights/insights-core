"""
Ansible - Parsers relates to Ansible
====================================

Below Parser is included in this module

AnsibleTelemetry - command "/usr/share/ansible/telemetry/telemetry.py"
----------------------------------------------------------------------
"""

import json

from insights import CommandParser, parser
from insights.core.exceptions import SkipComponent, ParseException
from insights.specs import Specs


@parser(Specs.ansible_telemetry)
class AnsibleTelemetry(CommandParser, list):
    """
    Parse the output of command "/usr/share/ansible/telemetry/telemetry.py".

    Sample output of the command is in NDJSON format::

        {"collections":{"ansible.builtin":{"resources":{"action":{"ansible.builtin.command":13}},"version":"*"}},"ansible_core":{"version":"2.18.9rc1"}}
        {"collections":{"ansible.builtin":{"resources":{"action":{"ansible.builtin.command":14}},"version":"*"}},"ansible_core":{"version":"2.19.9"}}

    Raises:
        SkipComponent: when nothing is parsed.
        ParseException: when any line is not parsable for JSON.

    Examples:
        >>> type(ansible_telemetry)
        <class 'insights.parsers.ansible.AnsibleTelemetry'>
        >>> ansible_telemetry[0]['collections']['ansible.builtin']['version'] == '*'
        True
        >>> ansible_telemetry[1]['ansible_core']['version'] == '2.19.9'
        True
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
                    raise ParseException("Invalid line: {0}".format(line))
                self.append(line_json) if line_json else None

        if len(self) == 0:  # pragma: no cover
            raise SkipComponent("Nothing parsable.")
