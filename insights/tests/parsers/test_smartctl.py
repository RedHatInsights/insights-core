import doctest

from insights.parsers import smartctl
from insights.parsers.smartctl import SmartctlHealth
from insights.tests import context_wrap

SMARTCTL_HEALTH = """
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
""".strip()


def test_smartctl_health():
    smartctl_health_info = SmartctlHealth(context_wrap(SMARTCTL_HEALTH))
    assert smartctl_health_info.data['device']['name'] == '/dev/sdb'
    assert smartctl_health_info.data['smart_status']['passed'] is True


def test_smartctl():
    env = {
        'smartctl_health': SmartctlHealth(context_wrap(SMARTCTL_HEALTH)),
    }
    failed, total = doctest.testmod(smartctl, globs=env)
    assert failed == 0
