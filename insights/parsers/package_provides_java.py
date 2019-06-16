#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
PackageProvidesJava - command ``/bin/echo {java_command_package}``
==================================================================

This command reads the output of the pre-command:

``for jp in `/bin/ps auxwww | grep java | grep -v grep| awk '{print $11}' | sort -u`; do echo $jp `readlink -e $jp | xargs rpm -qf`; done``

This command looks for all versions of 'java' running and tries to find the
RPM packages which provide them.  The running command and its package name
are stored as properties ``command`` and ``package`` of the object.

The reason why using above pre_command is that we need to record the links
between running_java_command and package which provides the java command. In
``ps aux`` output, we can only get what java command starts a java
application, instead of java package. Through this way, when there is jdk
bug, we can detect whether a running java application will be affected.

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

from insights import parser, CommandParser
from ..parsers import ParseException, SkipException
from insights.specs import Specs


@parser(Specs.package_provides_java)
class PackageProvidesJava(CommandParser):
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
