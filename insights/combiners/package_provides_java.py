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
PackageProvidesJavaAll - Combiner for packages which provide java
=================================================================

Combiner for collecting all the java command and the corresponding package name
which is parsed by the PackageProvidesJava parser.

"""

from .. import LegacyItemAccess
from insights.core.plugins import combiner
from insights.parsers.package_provides_java import PackageProvidesJava


@combiner(PackageProvidesJava)
class PackageProvidesJavaAll(LegacyItemAccess):
    """
    Combiner for collecting all the java command and the corresponding package
    name which is parsed by the PackageProvidesJava parser.
    It works as a ``dict`` with the java command as the key and the
    corresponding package name as the value.

    Examples:
        >>> PACKAGE_COMMAND_MATCH_1 = '''/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'''
        >>> PACKAGE_COMMAND_MATCH_2 = '''/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'''
        >>> pack1 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_1))
        >>> pack2 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_2))
        >>> shared = [{PackageProvidesJavaAll: [pack1, pack2]}]
        >>> packages = shared[PackageProvidesJavaAll]
        >>> packages.running_javas
        ['/usr/lib/jvm/jre/bin/java',
         '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java']
        >>> packages.get_package("/usr/lib/jvm/jre/bin/java")
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'
        >>> packages.get("/usr/lib/jvm/jre/bin/java")
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'
        >>> packages["/usr/lib/jvm/jre/bin/java"]
        'java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64'

    """

    def __init__(self, package_provides_java):
        self.data = {}
        for pkg in package_provides_java:
            self.data[pkg.command] = pkg.package
        super(PackageProvidesJavaAll, self).__init__()

    @property
    def running_javas(self):
        """
        Returns the list of java commands which are running on the system.
        """
        return self.data.keys()

    def get_package(self, java_command):
        """
        Returns the installed java package that provides the specified `java_command`.

        Parameters:
            java_command (str): The specified java command, e.g. found in ``ps`` command.

        Returns:
            (str): The package that provides the java command.
        """

        return self.data.get(java_command)
