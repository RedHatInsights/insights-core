"""
Facter - command ``/usr/bin/facter``
====================================

Module for the parsing of output from the ``facter`` command.
Data is avaliable as a dict for each line of the output.

Sample input data for the ``facter`` command looks like::

    architecture => x86_64
    bios_vendor => Phoenix Technologies LTD
    bios_version => 6.00
    domain => example.com
    facterversion => 1.7.6
    filesystems => btrfs,ext2,ext3,ext4,msdos,vfat,xfs
    fqdn => plin-w1rhns01.example.com
    hostname => plin-w1rhns01
    ipaddress => 172.23.27.50
    ipaddress_ens192 => 172.23.27.50
    ipaddress_lo => 127.0.0.1
    is_virtual => true
    kernel => Linux
    kernelmajversion => 3.10

Examples:
    >>> facts_info = shared[facter]
    >>> facts_info.kernelmajversion
    '3.10'
    >>> facts_info.domain
    'example.com'
    >>> facts_info.architecture
    'x86_64'
"""

from .. import parser, LegacyItemAccess, CommandParser
from insights.specs import Specs


@parser(Specs.facter)
class Facter(LegacyItemAccess, CommandParser):
    """Class for parsing ``facter`` command output.

    Attributes are the facts in each line of the command output.
    All facts may be accessed as ``obj.fact_name``. The ``get`` method is also
    provided to access any facts.
    """
    def parse_content(self, content):
        """
        Main parsing class method which stores all interesting data from the content.

        Args:
            content (context.content): Parser context content

        Returns:
            dict: dictionary with parsed data
        """
        self.fqdn = self.hostname = self.domain = None
        facts_info = {}
        for line in content:
            if ' => ' in line:
                key, value = [k.strip() for k in line.split('=>', 1)]
                facts_info[key] = value

        for k, v in facts_info.items():
            setattr(self, k, v)

        self.data = facts_info
