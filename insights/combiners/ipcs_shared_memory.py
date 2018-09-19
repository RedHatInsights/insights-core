"""
IPCS Shared Memory Segments
===========================

Combiner for parsing shared memory segments gotten from command ``ipcs``. It
uses the results of the ``IpcsM`` and ``IpcsMP`` parsers to get the size of the
shared memory of special ``PID``.

"""

from insights import combiner, LegacyItemAccess
from insights.parsers import ParseException
from insights.parsers.ipcs import IpcsM, IpcsMP


@combiner(IpcsM, IpcsMP)
class IpcsSharedMemory(LegacyItemAccess):
    """
    Class for parsing shared memory segments outputted by commands ``ipcs -m``
    and ``ipcs -m -p``.

    Typical output of command ``ipcs -m`` is::

        ------ Shared Memory Segments --------
        key        shmid      owner      perms      bytes      nattch     status
        0x0052e2c1 0          postgres   600        37879808   26
        0x0052e2c2 1          postgres   600        41222144   24

    Typical output of command ``ipcs -m -p`` is::

        ------ Shared Memory Creator/Last-op --------
        shmid      owner      cpid       lpid
        0          postgres   1833       23566
        1          postgres   1105       9882

    Examples:
        >>> type(ism)
        <class 'insights.combiners.ipcs_shared_memory.IpcsSharedMemory'>
        >>> ism.get_shm_size_of_pid('1105')
        41222144
    """
    def __init__(self, shm, shmp):
        if shm.data.keys() != shmp.data.keys():
            raise ParseException("The output of 'ipcs -m' doesn't match with 'ipcs -m -p'.")
        self.data = {}
        for s, v in shm.data.items():
            self.data[s] = v.copy()
            self.data[s].update(shmp[s])

    def get_shm_size_of_pid(self, pid):
        """
        Return the shared memory size of specified ``pid``.

        Returns:
            (int): size of the shared memory, 0 by default.
        """
        for _, v in self.data.items():
            if v['cpid'] == pid:
                return int(v['bytes'])
        return 0
