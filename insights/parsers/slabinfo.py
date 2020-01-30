"""
Slab allocator's details.
=========================

SlabInfo - File ``/proc/slabinfo``
----------------------------------
"""

from insights.specs import Specs
from insights import Parser, parser
from insights.parsers import SkipException


@parser(Specs.proc_slabinfo)
class SlabInfo(Parser):
    """
    Parse the content of the ``/proc/slabinfo`` file

    Sample input data looks like::

        slabinfo - version: 2.1
        # name            <active_objs> <num_objs> <objsize> <objperslab> <pagesperslab> : tunables <limit> <batchcount> <sharedfactor> : slabdata <active_slabs> <num_slabs> <sharedavail>
        sw_flow                0      0   1256   13    4 : tunables    0    0    0 : slabdata      0      0      0
        nf_conntrack_ffffffffaf313a40     12     12    320   12    1 : tunables    0    0    0 : slabdata      1      1      0
        xfs_dqtrx              0      0    528   15    2 : tunables    0    0    0 : slabdata      0      0      0
        xfs_dquot              0      0    488    8    1 : tunables    0    0    0 : slabdata      0      0      0
        xfs_ili             2264   2736    168   24    1 : tunables    0    0    0 : slabdata    114    114      0
        xfs_inode           4845   5120    960    8    2 : tunables    0    0    0 : slabdata    640    640      0
        xfs_efd_item          76     76    416   19    2 : tunables    0    0    0 : slabdata      4      4      0
        xfs_btree_cur         18     18    216   18    1 : tunables    0    0    0 : slabdata      1      1      0
        xfs_log_ticket        22     22    184   22    1 : tunables    0    0    0 : slabdata      1      1      0
        bio-3                 60     60    320   12    1 : tunables    0    0    0 : slabdata      5      5      0
        kcopyd_job             0      0   3312    9    8 : tunables    0    0    0 : slabdata      0      0      0
        dm_uevent              0      0   2608   12    8 : tunables    0    0    0 : slabdata      0      0      0
        dm_rq_target_io        0      0    136   30    1 : tunables    0    0    0 : slabdata      0      0      0
        ip6_dst_cache         72     72    448    9    1 : tunables    0    0    0 : slabdata      8      8      0
        RAWv6                 13     13   1216   13    4 : tunables    0    0    0 : slabdata      1      1      0
        UDPLITEv6              0      0   1216   13    4 : tunables    0    0    0 : slabdata      0      0      0
        UDPv6                 13     13   1216   13    4 : tunables    0    0    0 : slabdata      1      1      0
        tw_sock_TCPv6          0      0    256   16    1 : tunables    0    0    0 : slabdata      0      0      0
        TCPv6                 15     15   2112   15    8 : tunables    0    0    0 : slabdata      1      1      0
        cfq_queue              0      0    232   17    1 : tunables    0    0    0 : slabdata      0      0      0
        bsg_cmd                0      0    312   13    1 : tunables    10   20   30 : slabdata     40     50     60

    Examples:

        >>> type(pslabinfo)
        <class 'insights.parsers.slabinfo.SlabInfo'>
        >>> len(pslabinfo.data.keys())
        21
        >>> pslabinfo.slab_object('bsg_cmd', 'active_slabs')
        40
        >>> pslabinfo.slab_object('bsg_cmd', 'limit')
        10
    """

    def parse_content(self, content):
        self.data = {}
        self.__slab_version = None
        column = []
        row = []
        if not content:
            raise SkipException("No Contents")

        if 'slabinfo - version' in content[0]:
            self.__slab_version = content[0].split()[-1]
        else:
            raise SkipException("Invalid Contents")

        if "active_objs" in content[1]:
            line = content[1].split()
            column = [obj.replace('<', '').replace('>', '') for obj in line if obj not in ['#', ':', 'tunables', 'slabdata']]
        else:
            raise SkipException("Invalid Contents")

        for line in content[2:]:
            line = line.split()
            row = [obj for obj in line if obj not in ['#', ':', 'tunables', 'slabdata']]
            if column and row and len(column) == len(row):
                self.data[row[0]] = dict(zip(column, row))
                row = []
            else:
                raise SkipException("Invalid Contents")

    @property
    def slab_version(self):
        """
        (str): On success it will return the slab version else it will return `None`.
        """
        return self.__slab_version

    def slab_details(self, slab_name):
        """
        (dict): On success it will return the deatils of given slab, else it will return `None`.
        """
        return self.data.get(slab_name, None)

    def slab_object(self, slab_name, slab_obj):
        """
        (int): On success it will return the allocated slab object number, else it will return `0`.
        """
        slab_detail = self.data.get(slab_name, None)
        if slab_detail and slab_obj != 'name':
            return int(slab_detail.get(slab_obj, 0))
