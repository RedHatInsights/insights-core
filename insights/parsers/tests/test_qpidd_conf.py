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
