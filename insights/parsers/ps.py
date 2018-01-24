"""
PsAuxww - command ``ps auxww``
==============================

This module provides processing for the various outputs of the ``ps`` command.

Class ``PsAuxww`` parses the output of the ``ps auxww`` command.  A small
sample of the output of this command looks like::

    USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
    root      1661  0.0  0.0 126252  1392 ?        Ss   May31   0:04 /usr/sbin/crond -n
    root      1691  0.0  0.0  42688   172 ?        Ss   May31   0:00 /usr/sbin/rpc.mountd
    root      1821  0.0  0.0      0     0 ?        S    May31   0:29 [kondemand/0]
    root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 /usr/sbin/irqbalance --foreground
    user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
    root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 /usr/sbin/dhclient enp0s25

PsAuxww attempts to read the output of ``ps auxwww``, ``ps aux``, and ``ps
auxcww`` commands from archives.

Examples:
    >>> ps_data = '''
    ... USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    ... root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
    ... root      1661  0.0  0.0 126252  1392 ?        Ss   May31   0:04 /usr/sbin/crond -n
    ... root      1691  0.0  0.0  42688   172 ?        Ss   May31   0:00 /usr/sbin/rpc.mountd
    ... root      1821  0.0  0.0      0     0 ?        S    May31   0:29 [kondemand/0]
    ... root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 /usr/sbin/irqbalance --foreground
    ... user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
    ... root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 /usr/sbin/dhclient enp0s25
    ... '''
    >>> from insights.tests import context_wrap
    >>> shared = {PsAuxww: PsAuxww(context_wrap(ps_data))}
    >>> ps_info = shared[PsAuxww]
    >>> ps_info.running
    ['/usr/lib/systemd/systemd --switched-root --system --deserialize 22',
     '/usr/sbin/crond -n', '/usr/sbin/rpc.mountd', '[kondemand/0]',
     '/usr/sbin/irqbalance --foreground', 'bash', '/usr/sbin/dhclient enp0s25']
    >>> ps_info.cpu_usage('[kondemand/0]')
    '0.0'
    >>> ps_info.users('bash')
    {'user1': ['20160']}
    >>> ps_info.fuzzy_match('dhclient')
    True
    >>> ps_info.fuzzy_match('qemu')
    False
    >>> 'dhclient' in ps_info # strict match - exact command
    False
    >>> 'bash' in ps_info
    False
    >>> 'dhclient' in ps_info.cmd_names  # Just the command names but must match full command
    True
    >>> 'bash' in ps_info.cmd_names
    True
    >>> ps_info.data[3]
    {'USER': 'root', 'PID': '1691', '%CPU': '0.0', '%MEM': '0.0', 'VSZ': '42688',
     'RSS': '172', 'TTY': '?', 'STAT': 'Ss', 'START': 'May31', 'TIME': '0:00',
     'COMMAND': '/usr/sbin/rpc.mountd'}
    >>> ps_info.data[-1]['START']
    '10:09'
    >>> ps_info.search(STAT__contains='Z')
    []
    >>> sum(int(p['VSZ']) for p in ps_info)
    324132
"""
from .. import Parser, parser
from . import ParseException, parse_delimited_table, keyword_search
from insights.specs import Specs


@parser(Specs.ps_auxww)
class PsAuxww(Parser):
    """
    Class to parse ``ps auxww`` command output.

    Raises:
        ParseException: Raised if the heading line (starting with 'USER' and
            ending with 'COMMAND') is not found in the input.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the
            column headers and each item in the list represents a process.
        running (list): List of full command strings for each command
            including optional path and arguments, in order of listing in the
            `ps` output.
        cmd_names (list): List of just the command names, minus any path or
            arguments.

    """
    def __init__(self, *args, **kwargs):
        self.data = []
        self.running = set()
        self.cmd_names = set()
        self.services = []
        super(PsAuxww, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        raw_line_key = "_line"
        if any(line.startswith("USER") and line.endswith("COMMAND") for line in content):
            # parse_delimited_table allows short lines, but we specifically
            # want to ignore them.
            self.data = [
                row
                for row in parse_delimited_table(content, max_splits=10, raw_line_key=raw_line_key)
                if "COMMAND" in row
            ]
            # The above list comprehension assures all rows have a command.
            for proc in self.data:
                cmd = proc["COMMAND"]
                self.running.add(cmd)
                cmd_name = cmd.split(" ")[0].split("/")[-1]
                proc["COMMAND_NAME"] = cmd_name
                self.cmd_names.add(cmd_name)
                proc["ARGS"] = cmd.split(" ", 1)[1] if " " in cmd else ""
                self.services.append((cmd_name, proc["USER"], proc[raw_line_key]))
                del proc[raw_line_key]
        else:
            raise ParseException(
                "PsAuxww: Cannot find ps header line in output"
            )

    def __contains__(self, proc):
        return proc in self.running

    def __iter__(self):
        for row in self.data:
            yield row

    def running_pids(self):
        """
        Gives the list of process IDs in the order listed.

        Returns:
            list: the PIDs from the PID column.
        """
        return [row["PID"] for row in self.data if "PID" in row]

    def cpu_usage(self, proc):
        """
        Searches for the first command matching ``proc`` and returns its
        CPU usage as a string.

        Returns:
            str: the %CPU column corresponding to ``proc`` in COMMAND or
            ``None`` if ``proc`` is not found.

        .. note:: 'proc' must match the entire command and arguments.
        """
        for row in self.data:
            if proc == row["COMMAND"]:
                return row["%CPU"]

    def users(self, proc):
        """
        Searches for all users running a given command.

        Returns:
            dict: each username as a key to a list of PIDs (as strings) that
            are running the given process.

        .. note:: 'proc' must match the entire command and arguments.
        """
        ret = {}
        for row in self.data:
            if proc == row["COMMAND"]:
                if row["USER"] not in ret:
                    ret[row["USER"]] = []
                ret[row["USER"]].append(row["PID"])
        return ret

    def fuzzy_match(self, proc):
        """
        Are there any commands that contain the given text?

        Returns:
            boolean: ``True`` if the word ``proc`` appears in the COMMAND column.

        .. note:: 'proc' can match anywhere in the command path, name or
            arguments.
        """
        return any(proc in row['COMMAND'] for row in self.data)

    def search(self, **kwargs):
        """
        Search the process list for matching rows based on key-value pairs.

        This uses the :py:func:`insights.parsers.keyword_search` function for
        searching; see its documentation for usage details.  If no search
        parameters are given, no rows are returned.

        Returns:
            list: A list of dictionaries of processes that match the given
            search criteria.

        Examples:
            >>> ps.search(COMMAND__contains='java')
            >>> ps.search(USER='root', COMMAND__contains='watchdog')
            >>> ps.search(TTY='pts/0')
            >>> ps.search(STAT__contains='Z')
        """
        return keyword_search(self.data, **kwargs)


@parser(Specs.ps_auxcww)
class PsAuxcww(PsAuxww):
    pass


@parser(Specs.ps_aux)
class PsAux(PsAuxww):
    pass
