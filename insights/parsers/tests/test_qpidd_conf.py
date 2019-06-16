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

import doctest

from insights.parsers import qpidd_conf
from insights.parsers.qpidd_conf import QpiddConf
from insights.tests import context_wrap

QPIDD_CONF = """
# Configuration file for qpidd. Entries are of the form:
# name=value
#
# (Note: no spaces on either side of '='). Using default settings:
# "qpidd --help" or "man qpidd" for more details.
#cluster-mechanism=ANONYMOUS
log-enable=error+
log-to-syslog=yes
auth=no
require-encryption=yes
ssl-require-client-authentication=yes
ssl-port=5671
ssl-cert-db=/etc/pki/katello/nssdb
ssl-cert-password-file=/etc/pki/katello/nssdb/nss_db_password-file
ssl-cert-name=broker

interface=lo
"""


def test_qpidd_conf():
    qpidd_conf = QpiddConf(context_wrap(QPIDD_CONF))
    assert qpidd_conf['auth'] == 'no'
    assert ('require-encryption' in qpidd_conf) is True


def test_qpidd_conf_doc_examples():
    env = {
        'qpidd_conf': QpiddConf(context_wrap(QPIDD_CONF)),
    }
    failed, total = doctest.testmod(qpidd_conf, globs=env)
    assert failed == 0
