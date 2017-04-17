"""
Ipcs Semaphores
===============

Shared reducer for parsing all semaphores. It uses the results of the
``IpcsS`` and ``IpcsSI`` mappers to collect complete semaphore information,and
use ``PsAuxcww`` mappers to determine if one semaphore is orphan.

"""

from falafel.core.plugins import reducer
from falafel.mappers.ps import PsAuxcww
from falafel.mappers.ipcs_sem import IpcsS, IpcsSI


class IpcsSemaphore(object):
    """
    Class for holding information about one semaphore.

    """
    def __init__(self, data):
        self.semid = None
        """str: Semaphore ID."""
        self.owner = None
        """str: Owner of the semaphore."""
        self.is_orphan = False
        """bool: Is it an orphan semaphore?"""
        self.pid_list = []
        """list: List of the related PID."""

        for k, v in data.iteritems():
            setattr(self, k, v)


@reducer(requires=[IpcsS, IpcsSI, PsAuxcww], shared=True)
class IpcsSemaphores(object):
    """
    Class for parsing all semaphores. Will generate IpcsSemaphore objects for
    each semaphores.

    Below is the logic to determine if semaphore an orphan::

    - PID=0 does not included in the related PID
    - Related PID cannot be found in running PIDs

    Examples:
        >>> oph_sem = shared[IpcsSemaphores]
        >>> oph_sem.count_of_all_sems()
        4
        >>> oph_sem.count_of_all_sems(owner='apache')
        3
        >>> oph_sem.count_of_orphan_sems()
        2
        >>> oph_sem.count_of_orphan_sems('apache')
        1
        >>> oph_sem.get_sem('65536')
        <IpcsSemaphore object at 0x7ffa907bda10>

    """
    def __init__(self, local, shared):
        ps = shared[PsAuxcww]
        sem_s = shared[IpcsS]
        sem_si = shared[IpcsSI]

        pids = ps.running_pids()
        self._all_sems = {}
        self._orphan_sems = []
        for sem in sem_si:
            semid = sem.semid
            pid_list = sem.pid_list
            data = sem_s.get(sem.semid)
            data['pid_list'] = pid_list
            # check if it is orphan
            is_orphan = False
            if '0' not in pid_list and all(p not in pids for p in pid_list):
                is_orphan = True
            data['is_orphan'] = is_orphan
            sem_obj = IpcsSemaphore(data)
            self._all_sems[semid] = sem_obj
            if is_orphan:
                self._orphan_sems.append(sem_obj)

    def count_of_all_sems(self, owner=None):
        """
        Return the count of all semaphores by default, when ``owner`` is
        provided return the count of semaphores belong to ``owner``.

        Parameters:
            owner(str): Owner of semaphores.

        Returns:
            (int): the count of semaphores.
        """
        if owner:
            cnt = 0
            for sem in self._all_sems.values():
                cnt += 1 if sem.owner == owner else 0
            return cnt
        return len(self._all_sems)

    def count_of_orphan_sems(self, owner=None):
        """
        Return the count of orphan semaphores by default, when ``owner`` is
        provided return the count of orphan semaphores belong to ``owner``.

        Parameters:
            owner(str): Owner of semaphores.

        Returns:
            (int): the count of orphan semaphores
        """
        if owner:
            cnt = 0
            for sem in self._orphan_sems:
                cnt += 1 if sem.owner == owner else 0
            return cnt
        return len(self._orphan_sems)

    def get_sem(self, semid):
        """
        Return an IpcsSemaphore instance which semid is ``semid``

        Returns:
            (IpcsSemaphore): the instance of IpcsSemaphore
        """
        return self._all_sems.get(semid)

    def __iter__(self):
        """
        (iterable): Iterate the semaphores in no order.
        """
        for sem in self._all_sems.values():
            yield sem
