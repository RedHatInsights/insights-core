"""
PackageProvidesCommand - commands ``/bin/echo {command_package}``
==========================================================
This command reads the output of the pre-command::

    for jp in `/bin/ps auxcww | grep <cmd> | grep -v grep| awk '{print $11}' | sort -u`; do echo $jp `readlink -e $jp | xargs rpm -qf`; done

This command looks for all versions of ``cmd`` running and tries to find the
RPM packages which provide them.  The running command and its package name
are stored as properties ``command`` and ``package`` of the object.
"""

from insights import parser, CommandParser
from insights.parsers import SkipException, ParseException
from insights.specs import Specs


class PackageProvidesCommand(CommandParser, dict):
    """
    Base class to parse the output of the following command::

        for jp in `/bin/ps auxcww | grep <cmd> | grep -v grep | awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done

    Raises:
        SkipException: When no such command detected running on this host.
        ParseException: When there is un-parseble line.
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
        return list(self.keys())

    @property
    def packages(self):
        return list(self.values())


@parser(Specs.package_provides_java)
class PackageProvidesJava(PackageProvidesCommand):
    """
    This Parser provides the packages which actually provide the ``java``
    commands running on the host.

    Typical output::

        /usr/bin/java java-11-openjdk-11.0.9.11-2.el8_3.x86_64
        /usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64

    Examples:
        >>> java_package.commands
        ['/usr/bin/java', '/usr/lib/jvm/jre/bin/java']
        >>> java_package.packages
        ['java-11-openjdk-11.0.9.11-2.el8_3.x86_64', 'java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64']
        >>> java_package['/usr/lib/jvm/jre/bin/java']
        'java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64'
    """
    pass


@parser(Specs.package_provides_httpd)
class PackageProvidesHttpd(PackageProvidesCommand):
    """
    This Parser provides the packages which actually provide the ``httpd``
    commands running on the host.


    Typical output::

        /usr/sbin/httpd httpd-2.4.22-7.el7.x86_64
        /opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64

    Examples:
        >>> httpd_package.commands
        ['/usr/sbin/httpd', '/opt/rh/httpd24/root/usr/sbin/httpd']
        >>> httpd_package.packages
        ['httpd-2.4.22-7.el7.x86_64', 'httpd24-httpd-2.4.34-7.el7.x86_64']
        >>> httpd_package['/usr/sbin/httpd']
        'httpd-2.4.22-7.el7.x86_64'
    """
    pass
