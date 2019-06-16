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

from insights.parsers.package_provides_java import PackageProvidesJava
from insights.combiners.package_provides_java import PackageProvidesJavaAll
from insights.tests import context_wrap

PACKAGE_COMMAND_MATCH_1 = """
/usr/lib/jvm/jre/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""
PACKAGE_COMMAND_MATCH_2 = """
/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""

PACKAGE_COMMAND_MATCH_3 = """
java java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64
"""


def test_packages_provide_java():
    pack1 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_1))
    pack2 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_2))
    pack3 = PackageProvidesJava(context_wrap(PACKAGE_COMMAND_MATCH_3))
    result = PackageProvidesJavaAll([pack1, pack2, pack3])
    assert sorted(result.running_javas) == sorted(
        ['/usr/lib/jvm/jre/bin/java',
         '/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java', 'java'])
    assert result[
               "/usr/lib/jvm/java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64/bin/java"] == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"
    assert result.get_package("/usr/lib/jvm/jre/bin/java") == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"
    assert result.get("/usr/lib/jvm/jre/bin/java") == "java-1.8.0-openjdk-headless-1.8.0.141-3.b16.el6_9.x86_64"
    assert result.get_package("/usr/lib/jre/bin/java") is None
    assert result.get("/usr/lib/jre/bin/java") is None
