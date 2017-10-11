"""
PackageProvidesJava - Command
=============================

    This parser reads the output from pre_command::

        ``for jp in `/bin/ps auxwww | grep java | grep -v grep| awk '{print $11}' | sort -u`; do echo $jp `readlink -e $jp | xargs rpm -qf`; done``

    and converts running_java_command and its package name into properties ``command`` and ``package``.
    The reason why using above pre_command is that we need to record the links between running_java_command
    and package which provides the java command. In ``ps aux`` output, we can only get what java command starts a
    java application, instead of java package.
    Through this way, when there is jdk bug, we can detect whether a running java application will be affected.


    Typical contents of the pre_command::

        /usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64

    Parsed result::

        self.command = "/usr/lib/jvm/jre/bin/java"
        self.package = "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"

    Examples:

        >>> command_package = shared[PackageProvidesJava]
        >>> command_package.command
        '/usr/lib/jvm/jre/bin/java'
        >>> command_package.package
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'

    Raises:
        insights.parsers.ParseException: if there is no java application running

    Raises:
        insights.parsers.SkipException: if running java command is not provided by package installed through yum or rpm
"""

from insights import parser, Parser
from ..parsers import ParseException, SkipException


@parser('package_provides_java')
class PackageProvidesJava(Parser):
    """
    Parse the output of pre_command::

        ``for jp in `/bin/ps auxwww | grep java | grep -v grep| awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done``.

    Attributes:
        command (str): The java command that starts application.
        package (str): Java package that provides above java command.
    """

    def parse_content(self, content):
        if len(content) == 0:
            raise ParseException("Error: ", 'there is not java application running')
        l = content[0].split()
        if len(l) != 2:
            raise SkipException("Error: ",
                                'current running java command is not provided by package installed through yum or rpm')
        self.command = l[0]
        self.package = l[1]
