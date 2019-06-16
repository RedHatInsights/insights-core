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

from insights.parsers.jboss_version import JbossVersion
from insights.tests import context_wrap
import doctest
from insights.parsers import jboss_version

JBOSS_6 = """
Red Hat JBoss Enterprise Application Platform - Version 6.4.3.GA
""".strip()

JBOSS_7 = """
Red Hat JBoss Enterprise Application Platform - Version 7.1.0.Beta1
""".strip()


def test_jboss6():
    release6 = JbossVersion(context_wrap(JBOSS_6, path='/home/test/jboss/jboss-eap-6.4/version.txt'))
    assert release6.file_path == '/home/test/jboss/jboss-eap-6.4/version.txt'
    assert release6.raw == JBOSS_6
    assert release6.major == 6
    assert release6.minor == 4
    assert release6.version == "6.4.3"
    assert release6.code_name == "GA"
    assert release6.release == 3


def test_jboss7():
    release7 = JbossVersion(context_wrap(JBOSS_7, path='/home/test/jboss/jboss-eap-7.1/version.txt'))
    assert release7.file_path == '/home/test/jboss/jboss-eap-7.1/version.txt'
    assert release7.raw == JBOSS_7
    assert release7.major == 7
    assert release7.minor == 1
    assert release7.version == "7.1.0"
    assert release7.code_name == "Beta1"
    assert release7.release == 0


def test_jboss_version_doc_examples():
    env = {
        'JbossVersion': JbossVersion,
        'jboss_version': JbossVersion(context_wrap(JBOSS_6,
                                                   path='/home/test/jboss/jboss-eap-6.4/version.txt'))
    }
    failed, total = doctest.testmod(jboss_version, globs=env)
    assert failed == 0
