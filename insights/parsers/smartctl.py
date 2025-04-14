"""
smartctl - parser for smartctl commands
=======================================

Classes to parse the output of smartctl commands:

SmartctlHealth - /usr/sbin/smartctl -H -d scsi {devices}
--------------------------------------------------------
"""
import json

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.smartctl_health)
class SmartctlHealth(CommandParser):
    """
    Parse the output of command "smartctl -H -d scsi {devices}".

    Sample input::

        {
          "json_format_version": [
            1,
            0
          ],
          "smartctl": {
            "version": [
              7,
              2
            ],
            "svn_revision": "5155",
            "platform_info": "x86_64-linux-5.14.0-503.11.1.el9_5.x86_64",
            "build_info": "(local build)",
            "argv": [
              "smartctl",
              "-H",
              "-d",
              "scsi",
              "/dev/sdb",
              "-j"
            ],
            "exit_status": 0
          },
          "device": {
            "name": "/dev/sdb",
            "info_name": "/dev/sdb",
            "type": "scsi",
            "protocol": "SCSI"
          },
          "smart_status": {
            "passed": true
          }
        }

    Examples:
        >>> type(smartctl_health)
        <class 'insights.parsers.smartctl.SmartctlHealth'>
        >>> smartctl_health.data['smart_status']["passed"]
        True

    """
    def parse_content(self, content):
        self.data = json.loads(' '.join(content))
