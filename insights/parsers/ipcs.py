"""
IPCS commands
=============

Shared parsers for parsing output of the ``ipcs`` commands.

IpcsM - command ``ipcs -m``
---------------------------

IpcsMP - command ``ipcs -m -p``
-------------------------------

IpcsS - command ``ipcs -s``
---------------------------

IpcsSI - command ``ipcs -s -i {semaphore ID}``
----------------------------------------------

"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipComponent
from insights.core.plugins import parser
from insights.parsers import get_active_lines, parse_delimited_table
from insights.specs import Specs


class IPCS(CommandParser):
    """
    Base class for parsing the output of `ipcs -X` command in which the `X`
    could be `m`, `s` or `q`.

    """

    def parse_content(self, content):
        # heading_ignore is first line we _don't_ want to ignore...
        ids = ['semid', 'shmid', 'msqid']
        table = parse_delimited_table(content, heading_ignore=['key'] + ids)
        if not table:
            raise SkipComponent('Nothing to parse.')
        id_s = [i for i in table[0] if i in ids]
        if not id_s or len(id_s) != 1:
            raise ParseException('Unexpected heading line.')
        id_ok = id_s[0]
        self.data = {}
        for item in table:
            self.data[item.pop(id_ok)] = item

    def __contains__(self, sid):
        """
        Check if ``sid`` is contained or not
        """
        return sid in self.data

    def __getitem__(self, sid):
        """
        Retrieves an item from the underlying data dictionary.
        """
        return self.data[sid]

    def get(self, sid, default=None):
        """Returns value of key ``item`` in self.data or ``default``
        if key is not present.

        Parameters:
            sid(str): Key to get from ``self.data``.
            default (str): Default value to return if key is not present.

        Returns:
            {dict}: the stored dict item, or the ``default`` if not found.

        """
        return self.data.get(sid, default)


@parser(Specs.ipcs_m)
class IpcsM(IPCS):
    """
    Class for parsing the output of `ipcs -m` command.

    Typical output of the command is::

        ------ Shared Memory Segments --------
        key        shmid      owner      perms      bytes      nattch     status
        0x0052e2c1 0          postgres   600        37879808   26

    Examples:
        >>> '0' in shm
        True
        >>> shm.get('0', {}).get('bytes')
        '37879808'
        >>> '2602' in shm
        False
        >>> shm.get('2602', {}).get('bytes')

    """
    pass


@parser(Specs.ipcs_m_p)
class IpcsMP(IPCS):
    """
    Class for parsing the output of `ipcs -m -p` command.

    Typical output of the command is::

        ------ Shared Memory Creator/Last-op --------
        shmid      owner      cpid       lpid
        0          postgres   1833       14111

    Examples:
        >>> '0' in shmp
        True
        >>> shmp.get('0').get('cpid')
        '1833'
    """
    pass


@parser(Specs.ipcs_s)
class IpcsS(IPCS):
    """
    Class for parsing the output of `ipcs -s` command.

    Typical output of the command is::

        ------ Semaphore Arrays --------
        key        semid      owner      perms      nsems
        0x00000000 557056     apache     600        1
        0x00000000 589825     apache     600        1
        0x00000000 131074     apache     600        1
        0x0052e2c1 163843     postgres   600        17
        0x0052e2c2 196612     postgres   600        17
        0x0052e2c3 229381     postgres   600        17
        0x0052e2c4 262150     postgres   600        17
        0x0052e2c5 294919     postgres   600        17
        0x0052e2c6 327688     postgres   600        17
        0x0052e2c7 360457     postgres   600        17
        0x00000000 622602     apache     600        1
        0x00000000 655371     apache     600        1
        0x00000000 688140     apache     600        1

    Examples:
        >>> '622602' in sem
        True
        >>> '262150' in sem
        True
        >>> sem.get('262150').get('owner')
        'postgres'
    """
    pass


@parser(Specs.ipcs_s_i)
class IpcsSI(CommandParser):
    """
    Class for parsing the output of `ipcs -s -i ##` command. ``##`` will be
    replaced with specific semid

    Typical output of the command is::

        # ipcs -s -i 65536

        Semaphore Array semid=65536
        uid=500  gid=501     cuid=500    cgid=501
        mode=0600, access_perms=0600
        nsems = 8
        otime = Sun May 12 14:44:53 2013
        ctime = Wed May  8 22:12:15 2013
        semnum     value      ncount     zcount     pid
        0          1          0          0          0
        1          1          0          0          0
        0          1          0          0          6151
        3          1          0          0          2265
        4          1          0          0          0
        5          1          0          0          0
        0          0          7          0          6152
        7          1          0          0          4390

    Examples:
        >>> semi.semid
        '65536'
        >>> semi.pid_list
        ['0', '2265', '4390', '6151', '6152']

    """

    def parse_content(self, content):
        # parse the output of `ipcs -s -i ##` command
        pids = set()
        self._semid = None
        for line in get_active_lines(content):
            line = line.strip()
            if line.startswith('Semaphore'):
                self._semid = line.split('=')[-1]
            elif self._semid and line[0].isdigit():
                pids.add(line.split()[-1])
        self._pids = sorted(list(pids))

    @property
    def semid(self):
        """
        Return the semaphore ID.

        Returns:
            str: the semaphore ID.
        """
        return self._semid

    @property
    def pid_list(self):
        """
        Return the ID list of the processes which use this semaphore.

        Returns:
            [list]: the processes' ID list
        """
        return self._pids
