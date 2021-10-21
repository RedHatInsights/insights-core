from insights.parsers.ipaupgrade_log import IpaupgradeLog
from insights.tests import context_wrap

from datetime import datetime

IPAUPGRADE_LOG = """
2017-08-07T07:36:50Z DEBUG Starting external process
2017-08-07T07:36:50Z DEBUG args=/bin/systemctl is-active pki-tomcatd@pki-tomcat.service
2017-08-07T07:36:50Z DEBUG Process finished, return code=0
2017-08-07T07:36:50Z DEBUG stdout=active
2017-08-07T07:41:50Z ERROR IPA server upgrade failed: Inspect /var/log/ipaupgrade.log and run command ipa-server-upgrade manually.
"""


def test_ipaupgrade_log():
    log = IpaupgradeLog(context_wrap(IPAUPGRADE_LOG))
    assert len(log.get('DEBUG')) == 4
    assert len(list(log.get_after(datetime(2017, 8, 7, 7, 37, 30)))) == 1
