"""
Ps - command ``ps auxww`` and others
====================================

This module provides processing for the various outputs of the ``ps`` command.
"""
from insights.core import CommandParser, ContainerParser
from insights.core.exceptions import ParseException
from insights.core.filters import add_filter
from insights.core.plugins import parser
from insights.parsers import keyword_search, parse_delimited_table
from insights.specs import Specs


def are_present(tags, line):
    """bool: Returns True if all tags are present in line."""
    return all(tag in line for tag in tags)


class Ps(CommandParser):
    """
    Template Class to parse ``ps`` command output.

    Raises:
        ParseException: Raised if the heading line (containing both ``user_name``
            and ``command_name``) is not found in the input.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the
            column headers and each item in the list represents a process.
        running (set): Set of full command strings for each command
            including optional path and arguments, in order of listing in the
            `ps` output.
        cmd_names (set): Set of just the command names, minus any path or
            arguments.
        services (list): List of tuples in format (cmd names, user/uid/pid, raw_line) for
            each command.
        pid_info (dict): Dictionary indexed by ``pid`` returning dict of process info.

    """
    command_name = "COMMAND_TEMPLATE"
    '''
    ``command_name`` is the name of the subclass specific command column from the header of
    ps output, the subclass must override it correspondingly
    '''
    user_name = "USER_TEMPLATE"
    '''
    ``user_name`` is the name of the subclass specificuser_name column from the header of
    ps output, the subclass must override it correspondingly
    '''
    max_splits = 0
    '''
    ``max_splits`` is the split number for the columns from the ps output,
    the subclass must override it correspondingly
    '''

    def __init__(self, *args, **kwargs):
        self.data = []
        self.running = set()
        self.cmd_names = set()
        self.services = []
        self.pid_info = {}
        super(Ps, self).__init__(*args, **kwargs)

    def parse_content(self, content):
        raw_line_key = "_line"
        header_line = next((l for l in content if are_present(tags=[self.user_name, self.command_name], line=l)), None)
        if header_line is not None:
            # parse_delimited_table allows short lines, but we specifically
            # want to ignore them.
            self.data = [
                row
                for row in parse_delimited_table(
                    content, heading_ignore=[header_line], max_splits=self.max_splits,
                    raw_line_key=raw_line_key
                )
                # skip the insights-client self grep process "grep -F .."
                if self.command_name in row and not row[self.command_name].startswith('grep -F ')
            ]
            # The above list comprehension assures all rows have a command.
            for proc in self.data:
                cmd = proc[self.command_name]
                self.running.add(cmd)
                cmd_name = cmd
                if cmd.startswith('/'):
                    cmd_name = cmd.split(None, 1)[0].split("/")[-1]
                elif ' ' in cmd:
                    cmd_name = cmd.split(None, 1)[0]
                proc["COMMAND_NAME"] = cmd_name
                self.cmd_names.add(cmd_name)
                proc["ARGS"] = cmd.split(" ", 1)[1] if " " in cmd else ""
                self.services.append((cmd_name, proc[self.user_name], proc[raw_line_key]))
                del proc[raw_line_key]

            pid = None
            stat = None
            threads = 0
            for row in self.data:
                _pid = row['PID']
                if _pid.isdigit():
                    if threads:
                        # Set the number of threads for the previous entry, and
                        # set the entry's stat to the stat of the last thread.
                        self.pid_info[pid].update({"STAT": stat, "threads": threads})

                    pid = _pid
                    self.pid_info[_pid] = row

                    stat = None
                    threads = 0
                else:
                    stat = row['STAT']
                    threads += 1
            else:
                # Check if there was a thread as the last row.
                if threads:
                    self.pid_info[pid].update({"STAT": stat, "threads": threads})

        else:
            raise ParseException(
                "{0}: Cannot find ps header line containing {1} and {2} in output".format(
                    self.__class__.__name__, self.user_name, self.command_name)
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
        Searches for all users running a given command.  If the
        user column is not present then returns an empty dict.

        Returns:
            dict: each username as a key to a list of PIDs (as strings) that
            are running the given process.
            ``{}`` if neither ``USER`` nor ``UID`` is found or ``proc`` is not found.

        .. note::
           'proc' must match the entire command and arguments.
        """
        valid_user_columns = ['USER', 'UID']
        ret = {}
        if self.user_name in valid_user_columns:
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

        .. note::
           'proc' can match anywhere in the command path, name or arguments.
        """
        return any(proc in row[self.command_name] for row in self.data)

    def number_occurences(self, proc):
        """
        Returns the number of occurencies of commands that contain given text

        Returns:
            int: The number of occurencies of commands with given text

        .. note::
           'proc' can match anywhere in the command path, name or arguments.
        """
        return len([True for row in self.data if proc in row[self.command_name]])

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
            >>> ps.search(COMMAND__contains='bash') == [
            ...    {'%MEM': '0.0', 'TTY': 'pts/3', 'VSZ': '108472', 'ARGS': '', 'PID': '20160', '%CPU': '0.0',
            ...     'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'user1', 'STAT': 'Ss', 'TIME': '0:00',
            ...     'COMMAND_NAME': 'bash', 'RSS': '1896'},
            ...    {'%MEM': '0.0', 'TTY': '?', 'VSZ': '9120', 'ARGS': '', 'PID': '20457', '%CPU': '0.0',
            ...     'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'root', 'STAT': 'Ss', 'TIME': '0:00',
            ...     'COMMAND_NAME': 'bash', 'RSS': '832'}
            ... ]
            True
            >>> ps.search(USER='root', COMMAND__contains='bash') == [
            ...    {'%MEM': '0.0', 'TTY': '?', 'VSZ': '9120', 'ARGS': '', 'PID': '20457', '%CPU': '0.0',
            ...     'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'root', 'STAT': 'Ss', 'TIME': '0:00',
            ...     'COMMAND_NAME': 'bash', 'RSS': '832'}
            ... ]
            True
            >>> ps.search(TTY='pts/3') == [
            ...    {'%MEM': '0.0', 'TTY': 'pts/3', 'VSZ': '108472', 'ARGS': '', 'PID': '20160', '%CPU': '0.0',
            ...     'START': '10:09', 'COMMAND': '/bin/bash', 'USER': 'user1', 'STAT': 'Ss', 'TIME': '0:00',
            ...     'COMMAND_NAME': 'bash', 'RSS': '1896'}
            ... ]
            True
            >>> ps.search(STAT__contains='Z') == [
            ...    {'%MEM': '0.0', 'TTY': '?', 'VSZ': '0', 'ARGS': '', 'PID': '1821', '%CPU': '0.0',
            ...     'START': 'May31', 'COMMAND': '[kondemand/0]', 'USER': 'root', 'STAT': 'Z', 'TIME': '0:29',
            ...     'COMMAND_NAME': '[kondemand/0]', 'RSS': '0'}
            ... ]
            True
        """
        return keyword_search(self.data, **kwargs)


add_filter(Specs.ps_auxww, "COMMAND")


@parser(Specs.ps_auxww)
class PsAuxww(Ps):
    """
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
        >>> ps_auxww.running == set([
        ...     '/bin/bash', '/usr/sbin/rpc.mountd', '/usr/lib/systemd/systemd --switched-root --system --deserialize 22',
        ...     '/usr/sbin/irqbalance --foreground', '/usr/sbin/dhclient enp0s25', '[kondemand/0]', '/usr/sbin/crond -n'
        ... ])
        True
        >>> ps_auxww.cpu_usage('[kondemand/0]')
        '0.0'
        >>> ps_auxww.users('/bin/bash') == {'root': ['20457'], 'user1': ['20160']}
        True
        >>> ps_auxww.fuzzy_match('dhclient')
        True
        >>> sum(int(p['VSZ']) for p in ps_auxww)
        333252
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

        .. note::
           'proc' must match the entire command and arguments.
        """
        for row in self.data:
            if proc == row[self.command_name]:
                return row["%CPU"]

    pass


add_filter(Specs.ps_ef, "CMD")


@parser(Specs.ps_ef)
class PsEf(Ps):
    """
    Class ``PsEf`` parses the output of the ``ps -ef`` command.  A small
    sample of the output of this command looks like::

        UID         PID   PPID  C STIME TTY          TIME CMD
        root          1      0  0 03:53 ?        00:00:06 /usr/lib/systemd/systemd --system --deserialize 15
        root          2      0  0 03:53 ?        00:00:00 [kthreadd]
        root       1803      1  5 03:54 ?        00:55:22 /usr/bin/openshift start master --config=/etc/origin/master/master-config.yaml --loglevel
        root       1969      1  3 03:54 ?        00:33:51 /usr/bin/openshift start node --config=/etc/origin/node/node-config.yaml --loglevel=2
        root       1995      1  0 03:54 ?        00:02:06 /usr/libexec/docker/rhel-push-plugin
        root       2078   1969  0 03:54 ?        00:00:00 journalctl -k -f
        root       7201      1  0 03:59 ?        00:00:00 /usr/bin/python /usr/libexec/rhsmd
        root     111434      1  0 22:32 ?        00:00:00 nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf
        nginx    111435 111434  0 22:32 ?        00:00:00 nginx: worker process

    PsEf attempts to read the output of ``ps -ef`` commands from archives.

    Examples:
        >>> type(ps_ef)
        <class 'insights.parsers.ps.PsEf'>
        >>> ps_ef.parent_pid("111435")
        ['111434', 'nginx: master process /usr/sbin/nginx -c /etc/nginx/nginx.conf']
        >>> ps_ef.users('nginx: worker process')
        {'nginx': ['111435']}
        >>> ps_ef.fuzzy_match('kthreadd')
        True
    """
    command_name = "CMD"
    user_name = "UID"
    max_splits = 7

    def parent_pid(self, pid):
        """
        Search for the parent pid of command matching ``pid`` and returns
        the parent pid.

        Returns:
            list: First one is the parent pid corresponding to ``pid`` in command and second one is parent command name.
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


add_filter(Specs.container_ps_aux, "COMMAND")


@parser(Specs.container_ps_aux)
class ContainerPsAux(ContainerParser, PsAuxww):
    """
    Class to parse the command `ps aux` from the containers.

    Sample input data::

        USER       PID %CPU %MEM     VSZ    RSS TTY      STAT START   TIME COMMAND
        root         1  0.0  0.0   19356   1544 ?        Ss   May31   0:01 /sbin/init
        root      1821  0.0  0.0       0      0 ?        S    May31   0:25 [kondemand/0]
        root      1864  0.0  0.0   18244    668 ?        Ss   May31   0:05 irqbalance --pid=/var/run/irqbalance.pid
        user1    20160  0.0  0.0  108472   1896 pts/3    Ss   10:09   0:00 bash
        root     20357  0.0  0.0    9120    760 ?        Ss   10:09   0:00 /sbin/dhclient -1 -q -lf /var/lib/dhclient/dhclient-extbr0.leases -pf /var/run/dhclient-extbr0.pid extbr0
        qemu     22673  0.8 10.2 1618556 805636 ?        Sl   11:38   1:07 /usr/libexec/qemu-kvm -name rhel7 -S -M rhel6.5.0 -enable-kvm -m 1024 -smp 2,sockets=2,cores=1,threads=1 -uuid 13798ffc-bc1e-d437-4f3f-2e0fa6c923ad
        tomcat    3662  1.0  5.7 2311488  58236 ?        Ssl  07:28   0:01 /usr/lib/jvm/jre/bin/java -classpath /usr/share/tomcat/bin/bootstrap.jar:/usr/share/tomcat/bin/tomcat-juli.jar:/usr/share/java/commons-daemon.jar -Dcatalina.base=/usr/share/tomcat -Dcatalina.home=/usr/share/tomcat -Djava.endorsed.dirs= -Djava.io.tmpdir=/var/cache/tomcat/temp -Djava.util.logging.config.file=/usr/share/tomcat/conf/logging.properties -Djava.util.logging.manager=org.apache.juli.ClassLoaderLogManager org.apache.catalina.startup.Bootstrap start

    Examples:
        >>> type(container_ps_aux)
        <class 'insights.parsers.ps.ContainerPsAux'>
        >>> container_ps_aux.container_id
        '2869b4e2541c'
        >>> container_ps_aux.image
        'registry.access.redhat.com/ubi8/nginx-120'
        >>> container_ps_aux.number_occurences("bash")
        1
    """
    pass


@parser(Specs.ps_eo)
class PsEo(Ps):
    """
    Class to parse the command `ps -eo pid,ppid,comm`

    Sample input data::

          PID  PPID COMMAND
            1     0 systemd
            2     0 kthreadd
            3     2 ksoftirqd/0
         2416     1 auditd
         2419  2416 audispd
         2421  2419 sedispatch
         2892     1 NetworkManager
         3172  2892 dhclient
         3871     1 master
         3886  3871 qmgr
        13724  3871 pickup
        15663     2 kworker/0:1
        16998     2 kworker/0:3
        17259     2 kworker/0:0
        18294  3357 sshd

    Examples:
        >>> type(ps_eo)
        <class 'insights.parsers.ps.PsEo'>
        >>> ps_eo.pid_info['1'] == {'PID': '1', 'PPID': '0', 'COMMAND': 'systemd', 'COMMAND_NAME': 'systemd', 'ARGS': ''}
        True
        >>> ps_eo.children('2') == [
        ...     {'PID': '3', 'PPID': '2', 'COMMAND': 'ksoftirqd/0', 'COMMAND_NAME': 'ksoftirqd/0', 'ARGS': ''},
        ...     {'PID': '15663', 'PPID': '2', 'COMMAND': 'kworker/0:1', 'COMMAND_NAME': 'kworker/0:1', 'ARGS': ''},
        ...     {'PID': '16998', 'PPID': '2', 'COMMAND': 'kworker/0:3', 'COMMAND_NAME': 'kworker/0:3', 'ARGS': ''},
        ...     {'PID': '17259', 'PPID': '2', 'COMMAND': 'kworker/0:0', 'COMMAND_NAME': 'kworker/0:0', 'ARGS': ''}
        ... ]
        True
    """
    command_name = 'COMMAND'
    user_name = 'PID'
    max_splits = 3

    def children(self, ppid):
        """list: Returns a list of dict for all rows with `ppid` as parent PID"""
        return [row for row in self.data if row['PPID'] == ppid]


add_filter(Specs.ps_alxwww, "COMMAND")


@parser(Specs.ps_alxwww)
class PsAlxwww(Ps):
    """
    Class to parse the command `ps alxwww`.  See method and attribute details
    in the ``Ps`` parser.

    Sample input data::

        F   UID   PID  PPID PRI  NI    VSZ   RSS WCHAN  STAT TTY        TIME COMMAND
        4     0     1     0  20   0 128292  6928 ep_pol Ss   ?          0:02 /usr/lib/systemd/systemd --switched-root --system --deserialize 22
        1     0     2     0  20   0      0     0 kthrea S    ?          0:00 [kthreadd]
        1     0     3     2  20   0      0     0 smpboo S    ?          0:00 [ksoftirqd/0]
        5     0     4     2  20   0      0     0 worker S    ?          0:00 [kworker/0:0]
        1     0     5     2   0 -20      0     0 worker S<   ?          0:00 [kworker/0:0H]
        1     0     6     2  20   0      0     0 worker S    ?          0:00 [kworker/u4:0]
        1     0     7     2 -100  -      0     0 smpboo S    ?          0:00 [migration/0]
        1     0     8     2  20   0      0     0 rcu_gp S    ?          0:00 [rcu_bh]

    Examples:
        >>> type(ps_alxwww)
        <class 'insights.parsers.ps.PsAlxwww'>
        >>> 'systemd' in ps_alxwww.cmd_names
        True
        >>> '/usr/lib/systemd/systemd --switched-root --system --deserialize 22' in ps_alxwww.running
        True
        >>> ps_alxwww.search(COMMAND_NAME__contains='systemd') == [{
        ...     'F': '4', 'UID': '0', 'PID': '1', 'PPID': '0', 'PRI': '20', 'NI': '0', 'VSZ': '128292', 'RSS': '6928',
        ...     'WCHAN': 'ep_pol', 'STAT': 'Ss', 'TTY': '?', 'TIME': '0:02',
        ...     'COMMAND': '/usr/lib/systemd/systemd --switched-root --system --deserialize 22',
        ...     'COMMAND_NAME': 'systemd', 'ARGS': '--switched-root --system --deserialize 22'
        ... }]
        True

    """
    command_name = 'COMMAND'
    user_name = 'UID'
    max_splits = 12

    pass


@parser(Specs.ps_eo_cmd)
class PsEoCmd(Ps):
    """
    Class to parse the command `ps -eo pid,args` where the
    datasource `ps_eo_cmd` trims off all args leaving only the full
    path to the command.

    Sample output from the ``ps -eo pid, args`` command::

        PID COMMAND
          1 /usr/lib/systemd/systemd --switched-root --system --deserialize 31
          2 [kthreadd]
         11 /usr/bin/python3 /home/user1/pythonapp.py
         12 [kworker/u16:0-kcryptd/253:0]

    Sample data after trimming by the datasource::

        PID COMMAND
          1 /usr/lib/systemd/systemd
          2 [kthreadd]
         11 /usr/bin/python3
         12 [kworker/u16:0-kcryptd/253:0]

    Examples:
        >>> type(ps_eo_cmd)
        <class 'insights.parsers.ps.PsEoCmd'>
        >>> ps_eo_cmd.running_pids() == ['1', '2', '11', '12']
        True
        >>> ps_eo_cmd.search(COMMAND__contains='python3') == [
        ...     {'PID': '11', 'COMMAND': '/usr/bin/python3', 'COMMAND_NAME': 'python3', 'ARGS': ''}
        ... ]
        True
    """
    command_name = 'COMMAND'
    user_name = 'PID'
    max_splits = 1
