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

from insights.combiners.tomcat_virtual_dir_context import TomcatVirtualDirContextCombined
from insights.parsers.tomcat_virtual_dir_context import TomcatVirtualDirContextFallback, \
    TomcatVirtualDirContextTargeted
from insights.tests import context_wrap

FOUND_1_FALLBACK = """
/usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_2_FALLBACK = """
/usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
/usr/share/tomcat6/webapps/whatever/META-INF/context.xml:className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_3_FALLBACK = """
/usr/share/tomcat/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
/usr/share/tomcat/conf/server.xml:"VirtualDirContext"
/usr/share/tomcat6/webapps/whatever/META-INF/context.xml:className="org.apache.naming.resources.VirtualDirContext"
""".strip()

NOT_FOUND_FALLBACK = """
""".strip()

ERRORS_1_FALLBACK = """
/bin/grep: No such file or directory
"""

ERRORS_2_FALLBACK = """
garbage garbage
"""

ERRORS_3_FALLBACK = """
/bin/grep: /usr/share/tomcat*: No such file or directory
"""

FOUND_1_TARGETED = """
/srv/tomcat/uportal/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_2_TARGETED = """
/srv/tomcat/uportal/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
/srv/tomcat/test/webapps/whatever/META-INF/context.xml:className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_3_TARGETED = """
/srv/tomcat/uportal/conf/server.xml:    <Resources className="org.apache.naming.resources.VirtualDirContext"
/srv/tomcat/uportal/conf/server.xml:"VirtualDirContext"
/srv/tomcat/whatever_Again/webapps/whatever/META-INF/context.xml:className="org.apache.naming.resources.VirtualDirContext"
""".strip()

FOUND_4_TARGETED = FOUND_3_FALLBACK

NOT_FOUND_TARGETED = """
""".strip()

ERRORS_1_TARGETED = """
/bin/grep: No such file or directory
"""

ERRORS_2_TARGETED = """
garbage garbage
"""

ERRORS_3_TARGETED = """
/bin/grep: /usr/share/tomcat*: No such file or directory
"""


def test_tomcat_virtual_dir_context_found():
    fallback = TomcatVirtualDirContextFallback(context_wrap(FOUND_1_FALLBACK))
    targeted = TomcatVirtualDirContextTargeted(context_wrap(FOUND_1_TARGETED))
    combined = TomcatVirtualDirContextCombined(fallback, [targeted])
    assert len(combined.data) == 2
    assert combined.data == {'/usr/share/tomcat/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
                             '/srv/tomcat/uportal/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
                             }


def test_tomcat_virtual_dir_context_missing_parser():
    fallback = TomcatVirtualDirContextFallback(context_wrap(FOUND_1_FALLBACK))
    combined = TomcatVirtualDirContextCombined(fallback, None)
    assert len(combined.data) == 1
    assert combined.data == {'/usr/share/tomcat/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
                             }

    targeted = TomcatVirtualDirContextTargeted(context_wrap(FOUND_1_TARGETED))
    combined = TomcatVirtualDirContextCombined(None, [targeted])
    assert len(combined.data) == 1
    assert combined.data == {'/srv/tomcat/uportal/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"'],
                             }


def test_tomcat_virtual_dir_context_combinations_found():
    fallback = TomcatVirtualDirContextFallback(context_wrap(FOUND_3_FALLBACK))
    targeted = TomcatVirtualDirContextTargeted(context_wrap(FOUND_3_TARGETED))
    combined = TomcatVirtualDirContextCombined(fallback, [targeted])
    assert len(combined.data) == 4
    assert combined.data == {'/srv/tomcat/uportal/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"',
                              '"VirtualDirContext"'],

                             '/srv/tomcat/whatever_Again/webapps/whatever/META-INF/context.xml':
                             ['className="org.apache.naming.resources.VirtualDirContext"'],

                             '/usr/share/tomcat/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"',
                              '"VirtualDirContext"'],

                             '/usr/share/tomcat6/webapps/whatever/META-INF/context.xml':
                             ['className="org.apache.naming.resources.VirtualDirContext"'],
                             }


def test_tomcat_virtual_dir_context_combinations_found_but_same():
    fallback = TomcatVirtualDirContextFallback(context_wrap(FOUND_3_FALLBACK))
    targeted = TomcatVirtualDirContextTargeted(context_wrap(FOUND_4_TARGETED))
    combined = TomcatVirtualDirContextCombined(fallback, [targeted])
    assert len(combined.data) == 2
    assert combined.data == {'/usr/share/tomcat/conf/server.xml':
                             ['    <Resources className="org.apache.naming.resources.VirtualDirContext"',
                              '"VirtualDirContext"'],

                             '/usr/share/tomcat6/webapps/whatever/META-INF/context.xml':
                             ['className="org.apache.naming.resources.VirtualDirContext"'],
                             }


def test_tomcat_virtual_dir_context_no_data():
    combined = TomcatVirtualDirContextCombined(None, {})
    assert combined.data == {}
