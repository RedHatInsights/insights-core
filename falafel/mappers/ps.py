"""
ps - Command
============

This module provides processing for the output of the ``ps`` command.  The specs
handled by this command inlude::

    "ps_aux"                    : CommandSpec("/bin/ps aux"),
    "ps_auxcww"                 : CommandSpec("/bin/ps auxcww"),
    "ps_auxwww"                 : SimpleFileSpec("sos_commands/process/ps_auxwww"),

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

Class ``PsAuxwww`` parses the output of the ``ps auxwww`` command.  Output of
this command is similar to the ``ps aux``.

All classes utilize the same base class ``ProcessList`` so the following
examples apply to all classes in this module.

Examples:
    >>> ps_info = shared[PsAuxcww]
    >>> ps_info.running
    ['init', 'kondemand/0', 'irqbalance', 'bash', 'dhclient', 'qemu-kvn', 'vdsm']
    >>> ps_info.cpu_usage('vdsm')
    '98.0'
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
from .. import Mapper, mapper, parse_table

SERVICE_RUNNING = 'SERVICE_RUNNING'
SERVICES_RUNNING = 'SERVICES_RUNNING'


class ProcessList(Mapper):
    """Base class implementing shared code."""

    @property
    def running(self):
        """list: Returns the list of values from the COMMAND column."""
        return [row["COMMAND"] for row in self.data if "COMMAND" in row]

    def cpu_usage(self, proc):
        """str: Returns the %CPU column corresponding to ``proc`` in COMMAND or
        ``None`` if ``proc`` is not found.
        """
        for row in self.data:
            if proc == row["COMMAND"]:
                return row["%CPU"]

    def fuzzy_match(self, proc):
        """boolean: Returns ``True`` if ``proc`` is in the COMMAND column."""
        return proc in "".join(self.running)

    def __contains__(self, proc):
        return proc in self.running

    def __iter__(self):
        for row in self.data:
            yield row


@mapper('ps_auxcww')
class PsAuxcww(ProcessList):
    """Class to parse ``ps auxcww`` command output.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process.

        services (list): List of tuples containing (service, user, parsed line) which is useful
                         for security rules and their debugging.

    Raises:
        ValueError: Raised if any error occurs parsing the content.
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
            raise ValueError("PsAuxcww: Unable to parse content: {} ({})".format(len(content),
                                                                                 content[0]))

    def parse_services(self, content):
        """
        Alternative parsing method which also stores whole line.

        Args:
             content (context.content): Mapper context content

        Returns:
            list: list ouf tuples containing (service, user, parsed line)
        """
        for line in content[1:]:  # skip header
            parts = line.split(None, 10)
            service, user = parts[10], parts[0]
            self.services.append((service, user, line))

    def service_is_running(self, service_name):
        """
        Check for running process name.

        The method stops when first occurrence of 'service_name' is found.

        Some daemons are not provided as system services - e.g samba, git - however, they may still
        be running.

        For debugging purposes returns the matched line.

        Args:
            service_name (str): service name to look for

        Returns:
            dict: the matched line in the following format, otherwise empty dict:
                  {SERVICE_RUNNING: line}
        """
        for service, user, line in self.services:
            if service == service_name:
                return {SERVICE_RUNNING: line}
        return {}

    def services_are_running(self, *service_names):
        """
        Check for running process names.

        Some daemons are not provided as system services - e.g samba, git - however, they may still
        be running.

        For debugging purposes returns the matched line.

        Args:
            *service_names (str): service names to look for

        Returns:
            dict: containing list of found service names and their matched lines in the following
                  format, otherwise empty dict:

                  {SERVICES_RUNNING: {service_1: [line_1, line_2], service_2: [line1]}
        """
        services = {}
        for service, user, line in self.services:
            if service in service_names:
                if service not in services:
                    services[service] = []
                services[service].append(line)
        if services:
            return {SERVICES_RUNNING: services}
        else:
            return {}


@mapper('ps_aux', ['STAP', 'keystone-all', 'COMMAND'])
class PsAux(ProcessList):
    """Class to parse ``ps aux`` command output.

    Output is filtered to only contain the header line and lines containing
    the string 'keystone-all'.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process. The command
            and its args (if any) are kept together in the COMMAND key.
    """

    def parse_content(self, content):
        if len(content) > 0 and "COMMAND" in content[0]:
            self.data = parse_table(content, max_splits=10)


@mapper('ps_auxwww')  # we don't want to filter the ps_auxwww file
class PsAuxwww(PsAux):
    """Class to parse ``ps auxwww`` command output.

    Attributes:
        data (list):  List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a process.
    """
    pass
