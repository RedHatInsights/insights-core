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
    root      1821  0.0  0.0      0     0 ?        Z    May31   0:29 [kondemand/0]
    root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 /usr/sbin/irqbalance --foreground
    user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 /bin/bash
    root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 /usr/sbin/dhclient enp0s25
    root     20457  0.0  0.0   9120   832 ?        Ss   10:09   0:00 /bin/bash

PsAuxww attempts to read the output of ``ps auxwww``, ``ps aux``, and ``ps
auxcww`` commands from archives.

Examples:
    >>> type(ps_auxww)
    <class 'insights.parsers.ps.PsAuxww'>
    >>> ps_auxww.running
    set(['/bin/bash', '/usr/sbin/rpc.mountd', '/usr/lib/systemd/systemd --switched-root --system --deserialize 22', '/usr/sbin/irqbalance --foreground', '/usr/sbin/dhclient enp0s25', '[kondemand/0]', '/usr/sbin/crond -n'])
    >>> ps_auxww.cpu_usage('[kondemand/0]')
    '0.0'
    >>> ps_auxww.users('/bin/bash')
    {'root': ['20457'], 'user1': ['20160']}
    >>> ps_auxww.fuzzy_match('dhclient')
    True
    >>> ps_auxww.fuzzy_match('qemu')
    False
    >>> 'dhclient' in ps_auxww # strict match - exact command
    False
    >>> 'bash' in ps_auxww
    False
    >>> 'dhclient' in ps_auxww.cmd_names  # Just the command names but must match full command
    True
    >>> 'bash' in ps_auxww.cmd_names
    True
    >>> ps_auxww.data[3]
    {'%MEM': '0.0', 'TTY': '?', 'VSZ': '0', 'ARGS': '', 'PID': '1821', '%CPU': '0.0', 'START': 'May31', 'COMMAND': '[kondemand/0]', 'USER': 'root', 'STAT': 'Z', 'TIME': '0:29', 'COMMAND_NAME': '[kondemand/0]', 'RSS': '0'}
    >>> ps_auxww.services[3]
    ('[kondemand/0]', 'root', 'root      1821  0.0  0.0      0     0 ?        Z    May31   0:29 [kondemand/0]')
    >>> ps_auxww.data[-1]['START']
    '10:09'
    >>> ps_auxww.search(STAT__contains='l')
    []
    >>> sum(int(p['VSZ']) for p in ps_auxww)
    333252
"""
from .. import Parser, parser
from . import ParseException, parse_delimited_table, keyword_search
from insights.specs import Specs
from insights.core.filters import add_filter


class PsTemplate(Parser):
    """
    Template Class to parse ``ps`` command output.

    Raises:
        ParseException: Raised if the heading line (starting with 'USER'/'UID' and
            ending with 'COMMAND'/'CMD') is not found in the input.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the
            column headers and each item in the list represents a process.
        running (set): Set of full command strings for each command
            including optional path and arguments, in order of listing in the
            `ps` output.
        cmd_names (set): Set of just the command names, minus any path or
            arguments.
        services (list): List of sets in format (cmd names, user/uid, raw_line) for
            each command.

    """
    # command_name means the command content in last row from the ps output.
    # The value is the name of last row, and it is global variable in child process.
    command_name = "COMMAND_TEMPLATE"
    # user_name means the user content in first row from the ps output.
    # The value is the name of first row, and it is global variable in child process.
    user_name = "USER_TEMPLATE"
    # max_splits means the split number for the rows from the ps output.
    # The value is the number of rows, and it is global variable in child process.
    max_splits = 0

    def __init__(self, *args, **kwargs):
        self.data = []
        self.running = set()
        self.cmd_names = set()
        self.services = []
        super(PsTemplate, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        raw_line_key = "_line"
        if any(line.lstrip().startswith(self.user_name) and line.rstrip().endswith(self.command_name) for line in content):
            # parse_delimited_table allows short lines, but we specifically
            # want to ignore them.
            self.data = [
                row
                for row in parse_delimited_table(
                    content, heading_ignore=[self.user_name], max_splits=self.max_splits,
                    raw_line_key=raw_line_key
                )
                if self.command_name in row
            ]
            # The above list comprehension assures all rows have a command.
            for proc in self.data:
                cmd = proc[self.command_name]
                self.running.add(cmd)
                cmd_name = cmd
                if cmd.startswith('/'):
                    cmd_name = cmd.split(" ")[0].split("/")[-1]
                proc["COMMAND_NAME"] = cmd_name
                self.cmd_names.add(cmd_name)
                proc["ARGS"] = cmd.split(" ", 1)[1] if " " in cmd else ""
                self.services.append((cmd_name, proc[self.user_name], proc[raw_line_key]))
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
            if proc == row[self.command_name]:
                if row[self.user_name] not in ret:
                    ret[row[self.user_name]] = []
                ret[row[self.user_name]].append(row["PID"])
        return ret

    def fuzzy_match(self, proc):
        """
        Are there any commands that contain the given text?

        Returns:
            boolean: ``True`` if the word ``proc`` appears in the command column.

        .. note:: 'proc' can match anywhere in the command path, name or
            arguments.
        """
        return any(proc in row[self.command_name] for row in self.data)

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
            >>> PsTemplate.search(COMMAND__contains='bash')
            [{'%MEM': '0.0', 'TTY': 'pts/3', 'VSZ': '108472', 'ARGS': '', 'PID': '20160', '%CPU': '0.0', 'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'user1', 'STAT': 'Ss', 'TIME': '0:00', 'COMMAND_NAME': 'bash', 'RSS': '1896'}, {'%MEM': '0.0', 'TTY': '?', 'VSZ': '9120', 'ARGS': '', 'PID': '20457', '%CPU': '0.0', 'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'root', 'STAT': 'Ss', 'TIME': '0:00', 'COMMAND_NAME': 'bash', 'RSS': '832'}]
            >>> PsTemplate.search(USER='root', COMMAND__contains='bash')
            [{'%MEM': '0.0', 'TTY': '?', 'VSZ': '9120', 'ARGS': '', 'PID': '20457', '%CPU': '0.0', 'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'root', 'STAT': 'Ss', 'TIME': '0:00', 'COMMAND_NAME': 'bash', 'RSS': '832'}]
            >>> PsTemplate.search(TTY='pts/3')
            [{'%MEM': '0.0', 'TTY': 'pts/3', 'VSZ': '108472', 'ARGS': '', 'PID': '20160', '%CPU': '0.0', 'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'user1', 'STAT': 'Ss', 'TIME': '0:00', 'COMMAND_NAME': 'bash', 'RSS': '1896'}]
            >>> PsTemplate.search(STAT__contains='Z')
            [{'%MEM': '0.0', 'TTY': '?', 'VSZ': '0', 'ARGS': '', 'PID': '1821', '%CPU': '0.0', 'START': 'May31', 'COMMAND': '[kondemand/0]', 'USER': 'root', 'STAT': 'Z', 'TIME': '0:29', 'COMMAND_NAME': '[kondemand/0]', 'RSS': '0'}]
        """
        return keyword_search(self.data, **kwargs)


add_filter(Specs.ps_auxww, "COMMAND")


@parser(Specs.ps_auxww)
class PsAuxww(PsTemplate):
    """
    Class to parse ``ps auxww`` command output.
    """
    command_name = "COMMAND"
    user_name = "USER"
    max_splits = 10

    def cpu_usage(self, proc):
        """
        Searches for the first command matching ``proc`` and returns its
        CPU usage as a string.

        Returns:
            str: the %CPU column corresponding to ``proc`` in command or
            ``None`` if ``proc`` is not found.

        .. note:: 'proc' must match the entire command and arguments.
        """
        for row in self.data:
            if proc == row[self.command_name]:
                return row["%CPU"]

    pass


add_filter(Specs.ps_ef, "CMD")


@parser(Specs.ps_ef)
class PsEf(PsTemplate):
    """
    Class to parse ``ps ef`` command output.
    """
    command_name = "CMD"
    user_name = "UID"
    max_splits = 7

    def parent_pid(self, pid):
        """
        Search for the parent pid of command matching ``pid`` and returns
        the parent pid.

        Returns:
            str: The parent pid corresponding to ``pid`` in command or
            ``None`` if ``proc`` is not found.
        """
        for row in self.data:
            if pid == row["PID"]:
                for sub_row in self.data:
                    if sub_row["PID"] == row["PPID"]:
                        return [row["PPID"], sub_row[self.command_name]]

    pass


@parser(Specs.ps_auxcww)
class PsAuxcww(PsAuxww):
    pass


add_filter(Specs.ps_aux, "COMMAND")


@parser(Specs.ps_aux)
class PsAux(PsAuxww):
    pass
