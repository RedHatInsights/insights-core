"""
PackageProvidesJava - command ``/bin/echo {java_command_package}``
==================================================================
This module parses the content that contains running instances of 'java' and
its corresponding RPM package which provide them. The running command and its
package name are stored as properties ``command`` and ``package`` of the object.

The reason why using above datasource is that we need to record the links
between running_java_command and package which provides the java command. In
``ps aux`` output, we can only get what java command starts a java
application, instead of java package. Through this way, when there is java
bug, we can detect whether a running java application will be affected.

Examples:
    >>> command_package.command
    '/usr/lib/jvm/jre/bin/java'
    >>> command_package.package
    'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'

Raises:
    insights.parsers.SkipException: if running java command is not provided by package installed through yum or rpm
"""

from insights import parser, PackageProvidesParser
from insights.specs import Specs


@parser(Specs.package_provides_java)
class PackageProvidesJava(PackageProvidesParser):
    """
    Parse the output of pre_command::

        ``for jp in `/bin/ps auxwww | grep java | grep -v grep| awk '{print $11}' | sort -u`; do echo "$jp `readlink -e $jp | xargs rpm -qf`"; done``.

    Attributes:
        command (str): The java command that starts application.
        package (str): Java package that provides above java command.
    """
    pass
