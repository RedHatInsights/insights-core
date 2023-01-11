"""
PackageProvidesCommand - Command ``/bin/echo {command_package}``
================================================================
"""
from insights.core import CommandParser
from insights.core.exceptions import ParseException, SkipException
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.package_provides_command)
class PackageProvidesCommand(CommandParser, dict):
    """
    Parser to parse the specified running commands and its provider packages.

    This parser will receive a list of string pairs which is generated by
    several @datasource and functions. The first string is the full path of the
    specified running ``command`` and the second string is the package that
    provides this command.  It works as a `dict` with the ``command`` as the
    key and the corresponding package name as the value.

    To check the provider package of the specified command, please add the
    command to the ``COMMANDS`` of :func:`insights.specs.default.DefaultSpecs.cmd_and_pkg`

    Sample output::

        /usr/bin/java java-11-openjdk-11.0.9.11-2.el8_3.x86_64
        /usr/sbin/httpd httpd-2.4.22-7.el7.x86_64
        /usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64
        /opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64

    Raises:
        SkipException: When no such command detected running on this host.
        ParseException: When there is un-parseble line.

    Example:
        >>> '/usr/lib/jvm/jre/bin/java' in cmd_package.commands
        True
        >>> 'java-11-openjdk-11.0.9.11-2.el8_3.x86_64' in cmd_package.packages
        True
        >>> '/usr/sbin/httpd' in cmd_package.commands
        True
        >>> 'httpd24-httpd-2.4.34-7.el7.x86_64' in cmd_package.packages
        True
        >>> cmd_package['/usr/lib/jvm/jre/bin/java']
        'java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64'
        >>> cmd_package['/usr/sbin/httpd']
        'httpd-2.4.22-7.el7.x86_64'
    """

    def parse_content(self, content):
        data = {}
        for line in content:
            l_sp = [l.strip() for l in line.split()]
            if len(l_sp) != 2:
                raise ParseException('Incorrect line: {0}'.format(line))
            data[l_sp[0]] = l_sp[1]

        if len(data) == 0:
            raise SkipException()

        self.update(data)

    @property
    def commands(self):
        """
        Returns the list of specified commands that are running on this host.
        """
        return list(self.keys())

    @property
    def packages(self):
        """
        Returns the list of the packages that provide the specified ``commands``.
        """
        return list(self.values())
