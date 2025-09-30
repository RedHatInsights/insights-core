"""
Ansible - Parsers relates to Ansible
====================================

Below Parser is included in this module

AnsibleTelemetry - command "/usr/share/ansible/telemetry/telemetry.py"
----------------------------------------------------------------------
"""

from insights import CommandParser, JSONParser, parser
from insights.specs import Specs


@parser(Specs.ansible_telemetry)
class AnsibleTelemetry(CommandParser, JSONParser):
    """
    Parse the output of command "/usr/share/ansible/telemetry/telemetry.py".

    Sample output of the command is in JSON format::

        {
          "collections":{
            "ansible.builtin":{
              "resources":{
                "action":{
                  "ansible.builtin.add_host":78,
                  "ansible.builtin.uri":147,
                  "ansible.builtin.set_fact":96,
                  "ansible.builtin.debug":30,
                  "ansible.builtin.find":2,
                  "ansible.builtin.file":6,
                  "ansible.builtin.template":2,
                  "ansible.builtin.command":13
                },
                "connection":{
                  "ansible.builtin.local":113,
                  "ansible.builtin.ssh":290
                }
              },
              "version":"*"
            }
          },
          "ansible_core":{
            "version":"2.18.9rc1"
          },
          "hosts":{
            "count":44
          }
        }

    Examples:
        >>> type(ansible_telemetry)
        <class 'insights.parsers.ansible.AnsibleTelemetry'>
        >>> ansible_telemetry['collections']['ansible.builtin']['version'] == '*'
        True
        >>> ansible_telemetry['ansible_core']['version'] == '2.18.9rc1'
        True
    """

    pass
