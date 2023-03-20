"""
Kernel dump configuration files
===============================

This module contains the following parsers:

KDumpConf - file ``/etc/kdump.conf``
------------------------------------

KexecCrashLoaded - file ``/sys/kernel/kexec_crash_loaded``
----------------------------------------------------------

KexecCrashSize - file ``/sys/kernel/kexec_crash_size``
------------------------------------------------------

"""
import re

from insights.core import LegacyItemAccess, Parser
from insights.core.exceptions import ParseException
from insights.core.plugins import parser
from insights.specs import Specs

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


@parser(Specs.kdump_conf)
class KDumpConf(Parser, LegacyItemAccess):
    """
    A dictionary like object for the values of the ``/etc/kdump.conf`` file.

    Attributes:

        lines (list): raw lines from the file, in order
        data (dict): a dictionary of options set in the data
        comments(list): fully commented lines
        inline_comments(list): lines containing inline comments
        target(tuple): target line parsed as a (x, y) tuple if set, else None

    The ``data`` property has two special behaviours:

    * If an option - e.g. ``blacklist`` - is repeated, its values are
      collected together in a list.  Options that only appear once have
      their values stored as is.
    * The ``options`` option is special - it appears in the form ``option
      module value``.  The ``options`` key in the data dictionary is therefore
      stored as a dictionary, keyed on the ``module`` name.

    The ``target`` property has following possibilities:

    * If target-line starts with any keyword in ['raw', 'ssh', 'net', 'nfs', 'nfs4'],
      return tuple (keyword, value).
    * If target-line is set with '<fs_type> <partation>',
      return tuple (<fs_type>, <partation>).
    * If target-line is not set, the target is default which is depending on
      what's mounted in the current system, return None instead of tuple here.

    Main helper functions:

    * ``options`` - the ``options`` value in the data(see above).

    Sample ``/etc/kdump.conf`` file::

        path /var/crash
        core_collector makedumpfile -c --message-level 1 -d 24
        default shell

    Examples:

        >>> kd.is_local_disk
        True
        >>> kd.is_ssh()
        False
        >>> 'path' in kd
        True
    """
    NET_COMMANDS = set(['nfs', 'net', 'ssh'])
    SUPPORTED_FS_TYPES = ['ext2', 'ext3', 'ext4', 'btrfs', 'xfs']

    def parse_content(self, content):
        lines = list(content)
        opt_kw = 'options'
        items = {opt_kw: {}}
        # Paul Wayper - 2017-03-27 - why do we care about comments?
        comments = []
        inline_comments = []

        for _line in content:
            line = _line.strip()
            if not line:
                continue
            # Ignore lines that are entirely comments
            if line.startswith('#'):
                comments.append(_line)
                continue
            # Remove comments
            if '#' in line:
                comment_start = line.index('#')
                inline_comments.append(_line)
                line = line[0:comment_start]

            # Settings of the form 'option value' where value is the rest of
            # the line.  No equals is expected here.
            lineparts = [s.strip() for s in line.split(None, 1)]
            # All options must have a value
            if len(lineparts) < 2:
                continue
            opt, value = (lineparts)

            if opt != opt_kw:
                # Some items can be repeated - if they are, create a list of
                # their values
                if opt in items:
                    # Append to the list, creating if necessary
                    if not isinstance(items[opt], list):
                        items[opt] = [items[opt]]
                    items[opt].append(value)
                else:
                    items[opt] = value
            else:
                # 'options' is special - it becomes a dictionary
                mod, rest = value.split(None, 1)
                items[opt_kw][mod] = rest.strip()

        self.lines = lines
        self.data = items
        self.comments = comments
        self.inline_comments = inline_comments
        self.target = self._parse_target()

    def options(self, module):
        """
        Returns the options for this module in the settings.

        Arguments:
            module(str): The module name

        Returns:
            (str) The module's options, or '' if either ``options`` or
              ``module`` is not found.
        """
        return self.get('options', {}).get(module, '')

    def _network_lines(self, net_commands=NET_COMMANDS):
        """
        A list of all the options in the given list of commands, defaulting
        to the list of network destinations for kernel dumps (i.e. 'ssh',
        'nfs', 'nfs4' and 'net').
        """
        return filter(None, [self.get(n) for n in net_commands])

    def get_ip(self, net_commands=NET_COMMANDS):
        """
        Find the first IP address in the given list of commands.  Uses
        ``_network_lines`` above to find the list of commands.  The first
        line that lists an IP address is returned, otherwise None is returned.
        """
        ip_re = re.compile(r'(\d{1,3}\.){3}\d{1,3}')
        for l in self._network_lines(net_commands):
            matched_ip = ip_re.search(l)
            if matched_ip:
                return matched_ip.group()

    def is_ssh(self):
        """
        Is the destination of the kernel dump an ssh connection?
        """
        return 'ssh' in self or ('net' in self and '@' in self['net'])

    def is_nfs(self):
        """
        Is the destination of the kernel dump a NFS or NFSv4 connection?
        """
        return (
            ('nfs' in self or 'nfs4' in self) or
            ('net' in self and '@' not in self['net'])
        )

    def get_hostname(self, net_commands=NET_COMMANDS):
        """
        Find the first host name in the given list of commands.  Uses
        ``_network_lines`` above to find the list of commands.  The first
        line that matches ``urlparse``'s definition of a host name is
        returned, or None is returned.
        """
        for l in self._network_lines(net_commands):
            # required for urlparse to interpret as host instead of
            # relative path
            if '//' not in l:
                l = '//' + l
            netloc = urlparse(l).netloc

            # strip user:pass@
            i = netloc.find('@')
            if i != -1:
                netloc = netloc[i + 1:]

            # strip port
            return netloc.rsplit(':', 1)[0]

    @property
    def ip(self):
        """
        Uses get_ip() above to give the first IP address found in the list of
        crash dump destinations.
        """
        return self.get_ip()

    @property
    def hostname(self):
        """
        Uses get_hostname() above to give the first host name found in the
        list of crash dump destinations.
        """
        return self.get_hostname()

    @property
    def using_local_disk(self):
        """
        Is kdump configured to only use local disk?

        Several target types:

        * If 'raw' is given, then the dump is local.
        * If 'ssh', 'net', 'nfs', or 'nfs4' is given, then the dump is NOT local.
        * If '<fs type> <partition>' is given, then the dump is local.
        * Otherwise, the dump is local.

        Since only one target could be set, the logic used here is checking
        if remote target is used, return True for not.
        """
        return not ('ssh' in self.data or 'net' in self.data or
                    'nfs' in self.data or 'nfs4' in self.data)

    def _parse_target(self):
        """
        More than one dump targets will lead to kudmp service start failure.
        Raise an exception here if more than one target is set here.
        https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/kernel_administration_guide/kernel_crash_dump_guide#sect-supported-kdump-targets
        """
        target = None
        keys = ['ssh', 'net', 'nfs', 'nfs4', 'raw'] + self.SUPPORTED_FS_TYPES
        for k in keys:
            if k in self.data:
                v = self.data[k]
                if isinstance(v, list):
                    raise ParseException("More than one %s type targets are\
                                         configured." % k)
                if target:
                    raise ParseException("More than one target is configured.")
                else:
                    target = (k, v)
        return target


@parser(Specs.kexec_crash_loaded)
class KexecCrashLoaded(Parser):
    """
    A simple parser to determine if a crash kernel (i.e. a second kernel
    capable of capturing the machine state should the main kernel crash) is
    present.

    This simply returns a set of whether the ``/sys/kernel/kexec_crash_loaded``
    file has the value ``1``.
    """

    def parse_content(self, content):
        if len(content) == 0:
            self.is_loaded = False
            return
        line = list(content)[0].strip()
        self.is_loaded = line == '1'


@parser(Specs.kexec_crash_size)
class KexecCrashSize(Parser):
    """
    Parses the `/sys/kernel/kexec_crash_size` file which tells the
    reserved memory size for the crash kernel.

    Attributes:
        size (int): reserved memory size for the crash kernel, or 0 if not found.
    """

    def parse_content(self, content):
        self.size = 0
        if len(content) == 0:
            return
        size = list(content)[0].strip()
        if size.isdigit():
            self.size = int(size)
