"""
PackageProvidesCommand - Combiner for ``package_provides`` parsers
==================================================================
Combiner for collecting all the running command and the corresponding RPM package name
which is parsed by the corresponding PackageProvides parsers.
"""
import os
from insights.core.plugins import combiner
from insights.parsers import SkipComponent
from insights.parsers.package_provides_httpd import PackageProvidesHttpd
from insights.parsers.package_provides_java import PackageProvidesJava


@combiner(optional=[PackageProvidesHttpd, PackageProvidesJava])
class PackageProvidesCommand(dict):
    """
    This combiner will receive a list of parsers containing information about a running command
    and information about the RPM that provides that command.  It will combine all of the data into
    a dictionary using command as the key and RPM info as the value.

    Sample output all commands (one parser for each line)::

        /usr/bin/java java-11-openjdk-11.0.9.11-2.el8_3.x86_64
        /usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-1.8.0.272.b10-3.el8_3.x86_64

        /usr/sbin/httpd httpd-2.4.22-7.el7.x86_64
        /opt/rh/httpd24/root/usr/sbin/httpd httpd24-httpd-2.4.34-7.el7.x86_64

    Example:
        >>> type(cmd_package)
        <class 'insights.combiners.package_provides.PackageProvidesCommand'>
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

    Raises:
        SkipComponent: Raised when no commands found
    """
    def __init__(self, httpd, java):
        data = {}
        if httpd is not None:
            for pkg in httpd:
                data[pkg.command] = pkg.package
        if java is not None:
            for pkg in java:
                data[pkg.command] = pkg.package
        if not data:
            raise SkipComponent()

        self.update(data)

    @property
    def commands(self):
        """
        list: Returns the list of all commands that have been collected.
        """
        return list(self.keys())

    @property
    def command_names(self):
        """
        set: Returns the set of all commands names without the path
            that have been collected.
        """
        return set([os.path.split(cmd)[-1] for cmd in self.keys()])

    @property
    def packages(self):
        """
        list: Returns the list of all packages for the collected commands.
        """
        return list(self.values())

    def commands_by_name(self, command_name):
        """
        list: Returns the list of the commands that have ``command_name``
            as the tail of the command path.
        """
        return [cmd for cmd in self.keys() if command_name == os.path.split(cmd)[-1]]

    def command_and_package_by_name(self, command_name):
        """
        dict: Returns the commands and RPM info as a dictionary
            that have ``command_name`` as the tail of the command path.
        """
        return dict([
            (cmd, self[cmd]) for cmd in self.commands_by_name(command_name)
            if command_name == os.path.split(cmd)[-1]
        ])
