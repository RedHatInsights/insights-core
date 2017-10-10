"""
ps - Command
============

This module provides processing for the output of the ``ps`` command.  The specs
handled by this command inlude::

    "ps_aux"                    : CommandSpec("/bin/ps aux"),
    "ps_auxcww"                 : CommandSpec("/bin/ps auxcww"),
    "ps_auxwww"                 : SimpleFileSpec("sos_commands/process/ps_auxwww"),
    "ps_axcwwo"                 : CommandSpec("/bin/ps axcwwo ucomm,%cpu,lstart"),

Class ``PsAuxcww`` parses the output of the ``ps auxcww`` command.  Sample
output of this command looks like::

    USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
    root         1  0.0  0.0  19356  1544 ?        Ss   May31   0:01 init
    root      1821  0.0  0.0      0     0 ?        S    May31   0:29 kondemand/0
    root      1864  0.0  0.0  18244   668 ?        Ss   May31   0:05 irqbalance
    user1    20160  0.0  0.0 108472  1896 pts/3    Ss   10:09   0:00 bash
    root     20357  0.0  0.0   9120   832 ?        Ss   10:09   0:00 dhclient
    qemu     22673  0.6 10.7 1618556 840452 ?      Sl   11:38   1:31 qemu-kvm
    vdsm     27323 98.0 11.3  9120    987 ?        Ss   10.01   1:31 vdsm

Class ``PsAux`` parses the output of the ``ps aux`` command which is filtered
to only contain lines with the strings 'STAT', 'keystone-all', and 'COMMAND'.
Output is similar to the ``ps auxcww`` command except that the `COMMAND`
column provides additional information about the command.

Class ``PsAuxwww`` parses the output of the ``ps auxwww`` command. Output of
this command is similar to the ``ps aux``.

Class ``PsAxcwwo`` parses the output of the ``ps axcwwo ucomm,%cpu,lstart``
command to provide full timestamp of service start time. Sample output of this
command looks like::

    COMMAND         %CPU                  STARTED
    systemd          0.0 Thu Dec  8 01:19:25 2016
    kthreadd         0.0 Thu Dec  8 01:19:25 2016
    ksoftirqd/0      0.0 Thu Dec  8 01:19:25 2016
    libvirtd         0.0 Wed Dec 28 05:59:04 2016
    vdsm             1.3 Wed Dec 28 05:59:06 2016

All classes utilize the same base class ``ProcessList`` so the following
examples apply to all classes in this module.

Examples:
    >>> ps_info = shared[PsAuxcww]
    >>> ps_info.running
    ['init', 'kondemand/0', 'irqbalance', 'bash', 'dhclient', 'qemu-kvn', 'vdsm']
    >>> ps_info.cpu_usage('vdsm')
    '98.0'
    >>> ps_info.users('qemu-kvm')
    {'qemu': ['22673']}
    >>> ps_info.fuzzy_match('qemu')
    True
    >>> 'bash' in ps_info
    True
    >>> ps_info.data[3]
    {'USER': 'user1', 'PID': '20150', '%CPU': '0.0', '%MEM': '0.0', 'VSZ': '108472',
     'RSS': '1896', 'TTY': 'pts/3', 'STAT': 'Ss', 'START': '10:09', 'TIME': '0:00',
     'COMMAND': 'bash'}
    >>> ps_info.data[3]['START']
    '10:09'
    >>> [p['COMMAND'] for p in ps_info]
    ['init', 'kondemand/0', 'irqbalance', 'bash', 'dhclient', 'qemu-kvn', 'vdsm']
"""
from .. import Parser, parser, parse_table
from insights.parsers import ParseException


class ProcessList(Parser):
    """Base class implementing shared code."""

    @property
    def running(self):
        """list: Returns the list of values from the COMMAND column."""
        return [row["COMMAND"] for row in self.data if "COMMAND" in row]

    def running_pids(self):
        """list: Returns the list of PIDs from the PID column."""
        return [row["PID"] for row in self.data if "PID" in row]

    def cpu_usage(self, proc):
        """str: Returns the %CPU column corresponding to ``proc`` in COMMAND or
        ``None`` if ``proc`` is not found.
        """
        for row in self.data:
            if proc == row["COMMAND"]:
                return row["%CPU"]

    def users(self, proc):
        """dict: Returns the dict of ``USER`` and ``PID`` column in format of
        ``{USER: (PID1, PID2)}`` corresponding to ``proc`` in COMMAND
        """
        ret = {}
        for row in self.data:
            if proc == row["COMMAND"]:
                if row["USER"] not in ret:
                    ret.update({row["USER"]: []})
                ret[row["USER"]].append(row["PID"])
        return ret

    def fuzzy_match(self, proc):
        """boolean: Returns ``True`` if ``proc`` is in the COMMAND column."""
        return proc in "".join(self.running)

    def __contains__(self, proc):
        return proc in self.running

    def __iter__(self):
        for row in self.data:
            yield row


@parser('ps_auxcww')
class PsAuxcww(ProcessList):
    """Class to parse ``ps auxcww`` command output.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process.

        services (list): List of tuples containing (service, user, parsed line) which is useful
                         for security rules and their debugging.

    Raises:
        ParseException: Raised if any error occurs parsing the content.
    """
    def __init__(self, *args, **kwargs):
        self.data = {}
        self.services = []
        super(PsAuxcww, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        if len(content) > 0 and "COMMAND" in content[0]:
            self.data = parse_table(content)
            self.parse_services(content)
        else:
            raise ParseException(
                    "PsAuxcww: Unable to parse content: {} ({})".format(
                        len(content), content))

    def parse_services(self, content):
        """
        Alternative parsing method which also stores whole line.

        Args:
             content (context.content): Parser context content

        Returns:
            list: list ouf tuples containing (service, user, parsed line)
        """
        for line in content[1:]:  # skip header
            parts = line.split(None, 10)
            if len(parts) > 10:
                service, user = parts[10], parts[0]
                self.services.append((service, user, line))


@parser('ps_aux', ['STAP', 'keystone-all', 'COMMAND', 'tomcat'])
class PsAux(ProcessList):
    """Class to parse ``ps aux`` command output.

    Output is filtered to only contain the header line and lines containing
    the strings 'keystone-all' and 'tomcat'.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process. The command
            and its args (if any) are kept together in the COMMAND key.
    """

    def parse_content(self, content):
        if len(content) > 0 and "COMMAND" in content[0]:
            self.data = parse_table(content, max_splits=10)
        else:
            self.data = []


@parser('ps_auxwww')  # we don't want to filter the ps_auxwww file
class PsAuxwww(PsAux):
    """Class to parse ``ps auxwww`` command output.

    Attributes:
        data (list):  List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process.
    """
    pass


@parser('ps_axcwwo')
class PsAxcwwo(ProcessList):
    """Class to parse ``ps axcwwo ucomm,%cpu,lstart`` command output.

    Colume "STARTED" provides full timestamp of service start time.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process.

    Raises:
        ParseException: Raised if any error occurs parsing the content.
    """

    def parse_content(self, content):
        if len(content) > 0 and "COMMAND" in content[0]:
            self.data = parse_table(content, max_splits=2)
        else:
            raise ParseException(
                    "PsAxcwwo: Unable to parse {} line(s) of content:({})".format(
                        len(content), content))
