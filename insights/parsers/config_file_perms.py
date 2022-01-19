"""
Configuration File Permissions parsers
======================================

Parsers included in this module are:

SshdConfigPerms - command ``/bin/ls -lH /etc/ssh/sshd_config``
--------------------------------------------------------------

Grub1ConfigPerms - command ``/bin/ls -lH /boot/grub/grub.conf``
---------------------------------------------------------------

Grub2ConfigPerms - command ``/bin/ls -lH /boot/grub2/grub.cfg``
---------------------------------------------------------------
"""

from insights.core import CommandParser
from insights.core.plugins import parser
from insights.specs import Specs
from insights.util.file_permissions import FilePermissions


class FilePermissionsParser(CommandParser, FilePermissions):
    """
    Base class for ``SshdConfigPerms``, ``Grub1ConfigPerms`` and ``Grub2ConfigPerms`` classes.

    Attributes:
        line (string): the line from the command output
    """

    def __init__(self, context):
        self.line = ""
        CommandParser.__init__(self, context)
        FilePermissions.__init__(self, self.line)

    def parse_content(self, content):
        non_empty_lines = [line for line in content if line]  # get rid of blank lines
        self.line = non_empty_lines[0]


@parser(Specs.sshd_config_perms)
class SshdConfigPerms(FilePermissionsParser):
    """
    Class for parsing ``/bin/ls -lH /etc/ssh/sshd_config`` command.

    Sample output of this command is::

        -rw-------. 1 root root 4179 Dec  1  2014 /etc/ssh/sshd_config

    Examples:
        >>> type(sshd_perms)
        <class 'insights.parsers.config_file_perms.SshdConfigPerms'>
        >>> sshd_perms.line
        '-rw-------. 1 root root 4179 Dec  1  2014 /etc/ssh/sshd_config'
    """

    def __init__(self, context):
        super(SshdConfigPerms, self).__init__(context)


@parser(Specs.grub1_config_perms)
class Grub1ConfigPerms(FilePermissionsParser):
    """
    Class for parsing ``/bin/ls -lH /boot/grub/grub.conf`` command.

    Sample output of this command is::

        -rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub/grub.conf

    Examples:
        >>> type(grub1_perms)
        <class 'insights.parsers.config_file_perms.Grub1ConfigPerms'>
        >>> grub1_perms.line
        '-rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub/grub.conf'
    """

    def __init__(self, context):
        super(Grub1ConfigPerms, self).__init__(context)


@parser(Specs.grub_config_perms)
class Grub2ConfigPerms(FilePermissionsParser):
    """
    Class for parsing ``/bin/ls -lH /boot/grub2/grub.cfg`` command.

    Sample output of this command is::

        -rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub2/grub.cfg

    Examples:
        >>> type(grub2_perms)
        <class 'insights.parsers.config_file_perms.Grub2ConfigPerms'>
        >>> grub2_perms.line
        '-rw-r--r--. 1 root root 4179 Dec  1  2014 /boot/grub2/grub.cfg'
    """

    def __init__(self, context):
        super(Grub2ConfigPerms, self).__init__(context)
