"""
VDOStatus
=========
Combiner for ``vdo status`` information.

This combiner uses the parser:
:class:`insights.parsers.vdo_status.VDOStatus`

This combiner includes GETTING these elements of ``vdo status``:
    * vdo slab size
    * vdo volumns
    * vdo data blocks used
    * vdo logical blocks used
    * vdo overhead blocks used
    * vdo physical blocks
    * vdo savings ratio
    * vdo physical used pct
    * vdo logical free savdings ratio pct
    * vdo physical free

    Examples:
        >>> type(vdo)
        <class 'insights.combiners.vdo_status_calculation.VDOStatusCalculation'>
        >>> vdo.get_slab_size('vdo1')
        '2G'
        >>> vdo.volumns
        ['vdo2', 'vdo1']
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
        >>> vdo.get_savings_ratio('vdo2')
        14.0
        >>> vdo.get_logical_free_savings_ratio_pct('vdo2')
        37333.29

    Attributes:

        volumns (list): The list the vdo volumns involved

        slab_size (int): The size of vdo slab size for specified vdo

        logical_size (int): The size of logical blocks for specified vdo

        logical_used (int): The size of logical blocks used for specified vdo

        physical_size (int): The size of physical blocks for specified vdo

        physical_used (int): The size of physical blocks used for specified vdo

        overhead_used (int): The size of overhead blocks used for specified vdo

    Raises:
        ParseException: When input content is not available to parse

"""

from insights.core.plugins import combiner
from insights.parsers.vdo_status import VDOStatus
from insights.parsers import ParseException


@combiner(VDOStatus)
class VDOStatusCalculation(object):
    """
    This combiner provides an interface to deal with the data of ``vdo status``
    """

    def __init__(self, vstatus, vol=None):
        try:
            self.data = vstatus.data
            self.volumns = vstatus.data['VDOs'].keys()
        except:
            raise ParseException("couldn't parse yaml")

        self.slab_size = None
        self.physical_size = None
        self.physical_used = None
        self.overhead_used = None
        self.logical_size = None
        self.logical_used = None

    def __read_key_sizes__(self, vol):
        dm_path = ('/dev/mapper/%s' % vol)
        mapper = self.data['VDOs'][vol]['VDO statistics'][dm_path]
        self.slab_size = self.data['VDOs'][vol]['Slab size']
        self.physical_size = mapper['physical blocks']
        self.physical_used = mapper['data blocks used']
        self.overhead_used = mapper['overhead blocks used']
        self.logical_size = mapper['logical blocks']
        self.logical_used = mapper['logical blocks used']

    def get_slab_size(self, vol):
        """str: slab size"""
        self.__read_key_sizes__(vol)
        return self.slab_size

    def get_all_volumns(self):
        """list: vdo volumns"""
        return self.volumns

    def get_physical_blocks(self, vol):
        """int: physical blocks size"""
        self.__read_key_sizes__(vol)
        return self.physical_size

    def get_physical_used(self, vol):
        """int: Returns size of physical blocks used"""
        self.__read_key_sizes__(vol)
        return self.physical_used

    def get_overhead_used(self, vol):
        """int: Returns size of overhead blocks used"""
        self.__read_key_sizes__(vol)
        return self.overhead_used

    def get_logical_blocks(self, vol):
        """int: Returns size of logical blocks"""
        self.__read_key_sizes__(vol)
        return self.logical_size

    def get_logical_used(self, vol):
        """int: Returns size of logical blocks used"""
        self.__read_key_sizes__(vol)
        return self.logical_used

    def get_logical_free(self, vol):
        """int: Returns size of logical free"""
        self.__read_key_sizes__(vol)
        return (self.logical_size - self.logical_used)

    def get_physical_free(self, vol):
        """int: Returns size of physical free"""
        self.__read_key_sizes__(vol)
        return (self.physical_size - self.overhead_used - self.physical_used)

    def get_savings_ratio(self, vol):
        """float: Returns savings ratio"""
        self.__read_key_sizes__(vol)
        if self.physical_used == 0:
            return 0
        else:
            pct = float(self.logical_used / self.physical_used)
            return round(pct, 2)

    def get_physical_used_pct(self, vol):
        """ float: Returns physical used ratio"""
        self.__read_key_sizes__(vol)
        pct = (self.physical_used + self.overhead_used) / self.physical_size
        return round(pct, 2)

    def get_logical_free_savings_ratio_pct(self, vol):
        """float: Returns logical free savings ratio"""
        self.__read_key_sizes__(vol)
        pct = (self.get_logical_free(vol) / self.get_savings_ratio(vol))
        return round(pct, 2)
