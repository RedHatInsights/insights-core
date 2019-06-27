"""
Kernel system control information
=================================

Shared parsers for parsing file ``/etc/sysctl.conf`` and command ``sysctl -a``.

Parsers included in this module are:

Sysctl - command ``sysctl -a``
------------------------------

SysctlConf - file ``/etc/sysctl.conf``
--------------------------------------

SysctlConfInitramfs - command ``lsinitrd``
------------------------------------------

"""
from .. import Parser, LogFileOutput, parser, LegacyItemAccess, CommandParser
from ..parsers import split_kv_pairs
from insights.specs import Specs


@parser(Specs.sysctl_conf)
class SysctlConf(Parser):
    """Parse `/etc/sysctl.conf` file

    Sample input::

        # sysctl.conf sample
        #
          kernel.domainname = example.com

        ; this one has a space which will be written to the sysctl!
          kernel.modprobe = /sbin/mod probe

    Attributes:
        data (OrderedDict): Dictionary containing key/value pairs for the lines in the
            configuration file.  Dictionary is in order keywords first
            appear in the lines.

    Examples:
        >>> type(sysctl_conf)
        <class 'insights.parsers.sysctl.SysctlConf'>
        >>> sysctl_conf.data['kernel.domainname']
        'example.com'
        >>> sysctl_conf.data['kernel.modprobe']
        '/sbin/mod probe'
    """

    def parse_content(self, content):
        # Valid comments are both # and ; so remove one locally,
        # other comments and blank lines are removed by split fxn.
        lines = [l for l in content if not l.strip().startswith(';')]
        self.data = split_kv_pairs(lines, ordered=True)


@parser(Specs.sysctl)
class Sysctl(LegacyItemAccess, CommandParser):
    """Parse the output of `sysctl -a` command.

    Sample input::

        kernel.domainname = example.com
        kernel.modprobe = /sbin/modprobe

    Examples:
        >>> type(sysctl)
        <class 'insights.parsers.sysctl.Sysctl'>
        >>> sysctl['kernel.domainname']
        'example.com'
        >>> sysctl.get('kernel.modprobe')
        '/sbin/modprobe'
        >>> 'kernel.modules_disabled' in sysctl
        False
    """

    def parse_content(self, content):
        self.data = split_kv_pairs(content)


@parser(Specs.sysctl_conf_initramfs)
class SysctlConfInitramfs(CommandParser, LogFileOutput):
    """Shared parser for the output of ``lsinitrd`` applied to kdump
    initramfs images to view ``sysctl.conf`` and ``sysctl.d``
    configurations.

    For now, the file is treated as raw lines (as a ``LogFileOutput``
    parser.  This is because the output of the command, applied to
    multiple files to examine multiple files does not seem to be
    unambiguously parsable.

    Since the only plugins requiring the file to date "grep out"
    certain strings, this approach will suffice.

    .. note::
        Please refer to its super-class :class:`insights.core.LogFileOutput`

    Sample input::

        initramfs:/etc/sysctl.conf
        ========================================================================
        # sysctl settings are defined through files in
        # /usr/lib/sysctl.d/, /run/sysctl.d/, and /etc/sysctl.d/.
        #
        # Vendors settings live in /usr/lib/sysctl.d/.
        # To override a whole file, create a new file with the same in
        # /etc/sysctl.d/ and put new settings there. To override
        # only specific settings, add a file with a lexically later
        # name in /etc/sysctl.d/ and put new settings there.
        #
        # For more information, see sysctl.conf(5) and sysctl.d(5).
        fs.inotify.max_user_watches=524288
        ========================================================================

        initramfs:/etc/sysctl.d/*.conf
        ========================================================================
        ========================================================================

    Examples:
        >>> type(sysctl_initramfs)
        <class 'insights.parsers.sysctl.SysctlConfInitramfs'>
        >>> sysctl_initramfs.get('max_user_watches')
        [{'raw_message': 'fs.inotify.max_user_watches=524288'}]

    """
    def parse_content(self, content):
        # Remove all blank lines and comment lines prior to parsing
        valid_lines = []
        for line in content:
            line = line.strip()
            if line and not (line.startswith('#') or line.startswith(';')):
                valid_lines.append(line)
        super(SysctlConfInitramfs, self).parse_content(valid_lines)
