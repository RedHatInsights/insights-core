"""
VDOStatus - command ``/usr/bin/vdo status``
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
            Device mapper status: 0 8370216 vdo /dev/sda5 albserver online cpu=2,bio=4,ack=1,bioRotationInterval=64
            Physical size: 7G
            Slab size: 2G
            Storage device: /dev/sda5
            VDO statistics:
              /dev/mapper/vdo1:
                overhead blocks used: 787140
                physical blocks: 1835008
                data blocks used: 0
          vdo2:
            Acknowledgement threads: 1
            Activate: enabled
            Device mapper status: 0 8370212 vdo /dev/sda6 albserver online cpu=2,bio=4,ack=1,bioRotationInterval=64
            VDO statistics:
              /dev/mapper/vdo1:
                1K-blocks: 7340032

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
        >>> dict(vdo['VDO status'])
        {'Date': '2019-07-24 20:48:16-04:00', 'Node': 'dell-m620-10.rhts.gsslab.pek2.redhat.com'}
        >>> vdo['VDOs']['vdo2']['Acknowledgement threads']
        1
        >>> vdo.get_slab_size_of_vol('vdo1')
        '2G'
        >>> vdo.volumns
        ['vdo1', 'vdo2']
        >>> vdo.get_physical_blocks_of_vol('vdo1')
        1835008
        >>> vdo.get_physical_used_of_vol('vdo1')
        0
        >>> vdo.get_physical_free_of_vol('vdo1')
        1047868
        >>> vdo.get_logical_used_of_vol('vdo1')
        0
        >>> vdo.get_overhead_used_of_vol('vdo1')
        787140

    Raises:
        ParseException: When input content is not available to parse

    Attributes:
        data (dict): the result parsed of 'vdo status'

    """

    def __get_dev_mapper__(self, vol):

        """
        Device mapper path of a specified vdo

        Args:
            vol: String of vdo volumne name

        Returns:
            dict: Device mapper information of a specified volumne

        Raises:
            KeyError: If KEYs doesn't exist
            ParseException: When input content is not available to parse
        """

        # Check validation for vol name, return KeyError if not exists
        try:
            self.data['VDOs'][vol]
        except:
            err_path = "['VDOs'][%s]" % (vol)
            raise KeyError('No key(s) named: %s in %s' % (vol, err_path))

        # Parse next layer of ['VDO statistics'] when vol exists.
        vs = self.data['VDOs'][vol]['VDO statistics']

        # No device mapper path when 'VDO statistics' value is a string of 'not available'
        if not isinstance(vs, dict):
            raise ParseException('Not available device mapper path in string \'%s\'' % vs)

        # Has device mapper path when 'VDO statistics' value is a dict
        return list(vs.values())[0]

    @property
    def volumns(self):
        """ list: List of the volumns in vdo status """
        return sorted(self.data['VDOs'].keys()) if 'VDOs' in self.data else []

    def get_slab_size_of_vol(self, vol):
        """
        The slab size of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            str: Slab size of specified vdo volumne
        """
        return self.data['VDOs'][vol]['Slab size']

    def get_physical_blocks_of_vol(self, vol):
        """
        The physical blocks of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: physical blocks size
        """
        dm = self.__get_dev_mapper__(vol)
        return dm['physical blocks']

    def get_physical_used_of_vol(self, vol):
        """
        The physical used blocks of a specified volumn

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: Returns size of physical blocks used
        """
        dm = self.__get_dev_mapper__(vol)
        return dm['data blocks used']

    def get_overhead_used_of_vol(self, vol):
        """
        The overhead used blocks of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: Returns size of overhead blocks used
        """
        dm = self.__get_dev_mapper__(vol)
        return dm['overhead blocks used']

    def get_logical_blocks_of_vol(self, vol):
        """
        The logical blocks of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: Returns size of logical blocks
        """
        dm = self.__get_dev_mapper__(vol)
        return dm['logical blocks']

    def get_logical_used_of_vol(self, vol):
        """
        The logical used blocks of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: Returns size of logical blocks used
        """
        dm = self.__get_dev_mapper__(vol)
        return dm['logical blocks used']

    def get_logical_free_of_vol(self, vol):
        """
        The logical free blocks of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: Returns size of logical free
        """
        return (self.get_logical_blocks_of_vol(vol) -
                self.get_logical_used_of_vol(vol))

    def get_physical_free_of_vol(self, vol):
        """
        The physical free blocks of a specified volumne

        Args:
            vol (str): The vdo volumne name specified

        Returns:
            int: Returns size of physical free
        """
        return (self.get_physical_blocks_of_vol(vol) -
                self.get_overhead_used_of_vol(vol) -
                self.get_physical_used_of_vol(vol))
