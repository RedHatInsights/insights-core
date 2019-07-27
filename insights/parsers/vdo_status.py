"""
VdoStatus - command ``/usr/bin/vdo status``
===========================================

Module for parsing the output of command ``vdo status``. The bulk of the
content is split on the colon and keys are kept as is.
"""

from insights import parser
from insights import CommandParser
from insights import YAMLParser
from insights.specs import Specs


@parser(Specs.vdo_status)
class VDOStatus(CommandParser, YAMLParser):
    """
    Class for parsing ``vdo status`` command output.

    Typical output of command ``vdo status`` looks like::

        VDO status:
          Date: '2019-07-27 04:40:40-04:00'
          Node: rdma-qe-04.lab.bos.redhat.com
        Kernel module:
          Loaded: true
          Name: kvdo
          Version information:
            kvdo version: 6.1.0.153
        Configuration:
          File: /etc/vdoconf.yml
          Last modified: '2019-07-26 05:07:48'
        VDOs:
          vdo1:
            Acknowledgement threads: 1
            Activate: enabled
            Bio rotation interval: 64
            Bio submission threads: 4
            Block map cache size: 128M
            Block map period: 16380
            Block size: 4096
            CPU-work threads: 2
            Compression: enabled
            Configured write policy: auto
            Deduplication: enabled
            Device mapper status: 0 8370216 vdo /dev/sda5 albserver online cpu=2,bio=4,ack=1,bioRotationInterval=64
            Physical size: 7G
            Physical threads: 1
            Slab size: 2G
            Storage device: /dev/sda5
            VDO statistics:
              /dev/mapper/vdo1:
                1K-blocks: 7340032
                1K-blocks available: 4191472
                1K-blocks used: 3148560
                512 byte emulation: false
                KVDO module bios used: 298288
                KVDO module bytes used: 3403856064
                KVDO module peak bio count: 298576
                KVDO module peak bytes used: 3403857992
                bios acknowledged discard: 0
                bios acknowledged flush: 0
                bios acknowledged fua: 0
                bios acknowledged partial discard: 0
                bios acknowledged partial flush: 0
                bios acknowledged partial fua: 0
                bios acknowledged partial read: 0
                bios acknowledged partial write: 0
                slab journal tail busy count: 0
                slab summary blocks written: 0
                slabs opened: 0
                slabs reopened: 0
                updates found: 0
                updates not found: 0
                ...
          vdo2:
            Acknowledgement threads: 1
            Activate: enabled
            ...
            VDO statistics:
              /dev/mapper/vdo1:
                1K-blocks: 7340032
                ...
    Examples:
        >>> type(vdo)
        <class 'insights.parsers.vdo_status.VDOStatus'>
        >>> vdo['Kernel module']['Name']
        'kvdo'
        >>> vdo['Configuration']['File']
        '/etc/vdoconf.yml'
        >>> vdo['VDOs']['vdo1']['Activate']
        'enabled'
        >>> vdo['VDOs']['vdo1']['VDO statistics']['/dev/mapper/vdo1']['1K-blocks']
        7340032
        >>> vdo['VDO status']
        {'Date': '2019-07-24 20:48:16-04:00', 'Node': 'dell-m620-10.rhts.gsslab.pek2.redhat.com'}
        >>> vdo['VDOs']['vdo2']['Acknowledgement threads']
        1

    Attributes:
        data (dict): the result parsed of 'vdo status'

    Raises:
        ParseException: When input content is not available to parse
    """
    pass
