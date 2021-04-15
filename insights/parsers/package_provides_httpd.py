"""
PackageProvidesHttpd - command ``/bin/echo {httpd_command_package}``
====================================================================

.. warning::

    This module is deprecated, please use
    :mod:`insights.parsers.package_provides` instead.

This module parses the content that contains running instances of 'httpd' and
its corresponding RPM package which provide them. The running command and its
package name are stored as properties ``command`` and ``package`` of the object.

The reason why using above datasource is that we need to record the links
between running_httpd_command and package which provides the httpd command. In
``ps aux`` output, we can only get what httpd command starts a httpd
application, instead of httpd package. Through this way, when there is httpd
bug, we can detect whether a running httpd application will be affected.

Examples:
    >>> package.command
    '/opt/rh/httpd24/root/usr/sbin/httpd'
    >>> package.package
    'httpd24-httpd-2.4.34-7.el7.x86_64'
"""

from insights import parser, CommandParser
from insights.specs import Specs
from ..parsers import SkipException
from insights.util import deprecated


@parser(Specs.package_provides_httpd)
class PackageProvidesHttpd(CommandParser):
    """
    .. warning::

        This Combiner is deprecated, please use
        :class:`insights.parsers.package_provides.PackageProvidesCommand` instead.

    Parse the content like '/opt/rh/httpd24/root/usr/sbin/httpd /usr/sbin/httpd'

    Attributes:
        command (str): The httpd command that starts application.
        package (str): httpd package that provides above httpd command.
    """

    def parse_content(self, content):
        deprecated(
            PackageProvidesHttpd,
            'Please use the :class:`insights.parsers.package_provides.PackageProvidesCommand` instead.'
        )
        if len(content) == 0:
            raise SkipException("Error: ", 'there is not httpd application running')
        l = content[0].split()
        if len(l) != 2:
            raise SkipException("Error: ",
                                'current running httpd command is not provided by package installed through yum or rpm')
        self.command = l[0]
        self.package = l[1]
