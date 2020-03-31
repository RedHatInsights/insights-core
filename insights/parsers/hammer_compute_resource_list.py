"""
HammerComputeResourceList - command ``hammer --interactive 0 --output json compute-resource list``
==================================================================================================

This parser reads the compute resource list of a Satellite server using hammer in JSON format.
It relies on the root user running the command and hammer to authenticate based on the hammer configuration file.
If the command is unable to authenticate then no compute resources will be shown and an erro flag will be recorded in the parser

Sample output from the ``hammer --interactive 0 --output json compute-resource list`` command::

    [
  {
    "Id": 1,
    "Name": "kvm-server",
    "Provider": "Libvirt"
  },
  {
    "Id": 4,
    "Name": "VMWARE",
    "Provider": "VMware"
  },
  {
    "Id": 3,
    "Name": "vmware67",
    "Provider": "VMware"
  }
    ]

Examples:

    >>> type(hammer_compute_resources_list)
    <class 'insights.parsers.hammer_compute_resource_list.HammerComputeResourceList'>
"""

from insights import parser, CommandParser
from insights.parsers import SkipException
from insights.specs import Specs
import json


@parser(Specs.hammer_compute_resource_list)
class HammerComputeResourceList(CommandParser):
    """
    Parse the JSON output from the ``hammer --interactive 0 --output json compute-resource list`` command.

    Raises:
        SkipException: When nothing is parsed or hammer auth fails

    Attributes:
        data(list): A list of the parsed output returned by `hammer compute resource list`
    """

    def parse_content(self, content):
        if not content:
            raise SkipException('No content or hammer auth failed.')
        self.data = json.loads(''.join(content))
