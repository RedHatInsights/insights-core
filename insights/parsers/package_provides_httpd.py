"""
PackageProvidesHttpd - command ``/bin/echo {httpd_command_package}``
====================================================================

This command reads the output of the pre-command:

``for jp in `/bin/ps auxwww | grep httpd | grep -v grep| awk '{print $11}' | sort -u`; do echo $jp | xargs rpm -qf`; done``

This command looks for all versions of 'httpd' running and tries to find the
RPM packages which provide them.  The running command and its package name
are stored as properties ``command`` and ``package`` of the object.

The reason why using above pre_command is that we need to record the links
between running_httpd_command and package which provides the httpd command. In
``ps aux`` output, we can only get what httpd command starts a httpd
application, instead of httpd package. Through this way, when there is httpd
bug, we can detect whether a running httpd application will be affected.

Typical contents of the pre_command::

    /usr/sbin/httpd httpd-2.4.6-88.el7.x86_64

Parsed result::

    self.command = '/usr/sbin/httpd'
    self.package = 'httpd-2.4.6-88.el7.x86_64'

Examples:
    >>> from insights.tests import context_wrap
    >>> PACKAGE_COMMAND_MATCH = "/usr/sbin/httpd httpd-2.4.6-88.el7.x86_64"
    >>> command_package = PackageProvidesHttpd(context_wrap(PACKAGE_COMMAND_MATCH))
    >>> command_package.command
    '/usr/sbin/httpd'
    >>> command_package.package
    'httpd-2.4.6-88.el7.x86_64'
"""

from insights import parser, CommandParser
from insights.specs import Specs
from ..parsers import SkipException


@parser(Specs.package_provides_httpd)
class PackageProvidesHttpd(CommandParser):
    """
    Parse the output of pre_command::

        ``for jp in `/bin/ps auxwww | grep httpd | grep -v grep| awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done``.

    Attributes:
        command (str): The httpd command that starts application.
        package (str): httpd package that provides above httpd command.
    """

    def parse_content(self, content):
        if len(content) == 0:
            raise SkipException("Error: ", 'there is not httpd application running')
        l = content[0].split()
        if len(l) != 2:
            raise SkipException("Error: ",
                                'current running httpd command is not provided by package installed through yum or rpm')
        self.command = l[0]
        self.package = l[1]
