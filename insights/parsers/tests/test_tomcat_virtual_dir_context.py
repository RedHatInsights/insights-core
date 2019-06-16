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

import pytest

from insights.parsers.tomcat_virtual_dir_context import TomcatVirtualDirContextFallback, TomcatVirtualDirContextTargeted
from insights.tests import context_wrap
from insights.parsers import SkipException

FOUND_1 = """
/usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_2 = """
/usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
/usr/share/tomcat6/webapps/whatever/META-INF/context.xml:className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_3 = """
/usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
/usr/share/tomcat/conf/server.xml:"VirtualDirContext"
/usr/share/tomcat6/webapps/whatever/META-INF/context.xml:className="org.apache.naming.resources.VirtualDirContext"
""".strip()

NOT_FOUND = """
""".strip()

ERRORS_2 = """
garbage garbage
"""


def test_tomcat_virtual_dir_context_found():
    for parser in [TomcatVirtualDirContextFallback, TomcatVirtualDirContextTargeted]:
        tomcat_virtual_dir_context = parser(context_wrap(FOUND_1))
        assert len(tomcat_virtual_dir_context.data) == 1
        assert tomcat_virtual_dir_context.data == {'/usr/share/tomcat/conf/server.xml':
                                                   ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
                                                   }

        tomcat_virtual_dir_context = parser(context_wrap(FOUND_2))
        assert len(tomcat_virtual_dir_context.data) == 2
        assert tomcat_virtual_dir_context.data == {'/usr/share/tomcat/conf/server.xml':
                                                   ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
                                                   '/usr/share/tomcat6/webapps/whatever/META-INF/context.xml':
                                                   ['className="org.apache.naming.resources.VirtualDirContext"'],
                                                   }

        tomcat_virtual_dir_context = parser(context_wrap(FOUND_3))
        assert len(tomcat_virtual_dir_context.data) == 2
        assert tomcat_virtual_dir_context.data == {'/usr/share/tomcat/conf/server.xml':
                                                   ['    <Resources className="org.apache.naming.resources.VirtualDirContext"',
                                                    '"VirtualDirContext"'],
                                                   '/usr/share/tomcat6/webapps/whatever/META-INF/context.xml':
                                                   ['className="org.apache.naming.resources.VirtualDirContext"'],
                                                   }


def test_tomcat_virtual_dir_context_not_found():
    for parser in [TomcatVirtualDirContextFallback, TomcatVirtualDirContextTargeted]:
        with pytest.raises(SkipException) as excinfo:
            parser(context_wrap(NOT_FOUND))
            assert 'VirtualDirContext not used.' in str(excinfo.value)


def test_tomcat_virtual_dir_context_exceptions():
    for parser in [TomcatVirtualDirContextFallback, TomcatVirtualDirContextTargeted]:
        with pytest.raises(SkipException) as excinfo:
            parser(context_wrap(ERRORS_2))
            assert 'VirtualDirContext not used.' in str(excinfo.value)
