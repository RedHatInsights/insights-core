"""
VdoStatus - command ``/usr/bin/vdo status``
===========================================

Module for parsing the output of command ``vdo status``. The bulk of the
content is split on the colon and keys are kept as is.

"""

from __future__ import division
from insights import parser
from insights import YAMLParser
from insights.specs import Specs
from insights.parsers import ParseException


@parser(Specs.vdo_status)
class VDOStatus(YAMLParser):
    """
    Class for parsing ``vdo status`` command output.

    This class includes GETTING following information of ``vdo status``::

        vdo slab size
        vdo volumns
        vdo data blocks used
        vdo logical blocks used
        vdo overhead blocks used
        vdo physical blocks
        vdo savings ratio
        vdo physical used pct
        vdo logical free savdings ratio pct
        vdo physical free


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
                logical blocks: 1046277
                logical blocks used: 0
                maximum VDO IO requests in progress: 9
                maximum dedupe queries: 0
                no space error count: 0
                operating mode: normal
                overhead blocks used: 787140
                physical blocks: 1835008
                data blocks used: 0
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
        >>> vdo.get_slab_size('vdo1')
        '2G'
        >>> vdo.volumns
        ['vdo1', 'vdo2']
        >>> vdo.get_physical_blocks('vdo1')
        1835008
        >>> vdo.get_physical_used('vdo1')
        0
        >>> vdo.get_physical_free('vdo1')
        1047868
        >>> vdo.get_logical_used('vdo1')
        0
        >>> vdo.get_overhead_used('vdo1')
        787140

    Attributes:

        data (dict): the result parsed of 'vdo status'

        volumns (list): The list the vdo volumns involved

        dmapper (dict): The dict of device mapper vdo under 'VDO statistics'

    Raises:
        ParseException: When input content is not available to parse

    """

    def __init__(self, content):
        YAMLParser.__init__(self, content)
        self.volumns = []
        try:
            keys = list(self.data['VDOs'].keys())
            keys.sort()
            self.volumns = keys
        except:
            raise ParseException("couldn't parse yaml")

    def __get_dev_mapper__(self, vol):
        try:
            dm_path = ('/dev/mapper/%s' % vol)
            return self.data['VDOs'][vol]['VDO statistics'][dm_path]
        except:
            raise ParseException("couldn't parse yaml")

    def get_all_volumns(self):
        """list: vdo volumns"""
        return self.volumns

    def get_slab_size(self, vol):
        """str: slab size"""
        return self.data['VDOs'][vol]['Slab size']

    def get_physical_blocks(self, vol):
        """int: physical blocks size"""
        dm = self.__get_dev_mapper__(vol)
        return dm['physical blocks']

    def get_physical_used(self, vol):
        """int: Returns size of physical blocks used"""
        dm = self.__get_dev_mapper__(vol)
        return dm['data blocks used']

    def get_overhead_used(self, vol):
        """int: Returns size of overhead blocks used"""
        dm = self.__get_dev_mapper__(vol)
        return dm['overhead blocks used']

    def get_logical_blocks(self, vol):
        """int: Returns size of logical blocks"""
        dm = self.__get_dev_mapper__(vol)
        return dm['logical blocks']

    def get_logical_used(self, vol):
        """int: Returns size of logical blocks used"""
        dm = self.__get_dev_mapper__(vol)
        return dm['logical blocks used']

    def get_logical_free(self, vol):
        """int: Returns size of logical free"""
        return (self.get_logical_blocks(vol) - self.get_logical_used(vol))

    def get_physical_free(self, vol):
        """int: Returns size of physical free"""
        return (self.get_physical_blocks(vol) - self.get_overhead_used(vol) - self.get_physical_used(vol))
