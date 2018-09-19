"""
IPCS commands
=============

Shared parsers for parsing output of the ``ipcs -s`` and ``ipcs -s -i``
commands.

IpcsS - command ``ipcs -s``
---------------------------

IpcsSI - command ``ipcs -s -i {semaphore ID}``
----------------------------------------------

"""
from insights.util import deprecated
from .. import parser, get_active_lines, CommandParser
from . import parse_delimited_table
from insights.specs import Specs


@parser(Specs.ipcs_s)
class IpcsS(CommandParser):
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
        >>> sem = shared[IpcsS]
        >>> '622602' in sem
        True
        >>> sem['622602']
        {'owner': 'apache', 'perms': '600', 'nsems': '1', 'key': '0x00000000'}
        >>> sem.get('262150')
        {'owner': 'postgres', 'perms': '600', 'nsems': '1', 'key': '0x00000000'}
    """
    def __init__(self, *args, **kwargs):
        deprecated(IpcsS, "Import IpcsS from insights.parsers.ipcs instead")
        super(IpcsS, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        # heading_ignore is first line we _don't_ want to ignore...
        table = parse_delimited_table(content, heading_ignore=['key'])
        data = map(lambda item: dict((k, v) for (k, v) in item.items()), table)
        self.data = {}
        for item in data:
            self.data[item.pop('semid')] = item

    def __contains__(self, semid):
        """
        Check if ``semid`` is contained or not
        """
        return semid in self.data

    def __getitem__(self, semid):
        """
        Retrieves an item from the underlying data dictionary.
        """
        return self.data[semid]

    def get(self, semid, default=None):
        """Returns value of key ``item`` in self.data or ``default``
        if key is not present.

        Parameters:
            item (str): Key to get from ``self.data``.
            default (str): Default value to return if key is not present.

        Returns:
            {dict}: the stored dict item, or the default if not found.

        """
        return self.data.get(semid, default)


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
        >>> sem = shared[IpcsSI]
        >>> sem.semid
        '65536'
        >>> sem.pid_list
        ['0', '2265', '4390', '6151', '6152']

    """
    def __init__(self, *args, **kwargs):
        deprecated(IpcsSI, "Import IpcsSI from insights.parsers.ipcs instead")
        super(IpcsSI, self).__init__(*args, **kwargs)

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
