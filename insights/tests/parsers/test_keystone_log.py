from insights.parsers.keystone_log import KeystoneLog
from insights.tests import context_wrap

from datetime import datetime

KEYSTONE_LOG = """
2016-11-09 14:31:48.681 1082 WARNING oslo_config.cfg [-] Option "rabbit_userid" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
2016-11-09 14:31:48.681 1082 WARNING oslo_config.cfg [-] Option "rabbit_password" from group "oslo_messaging_rabbit" is deprecated for removal.  Its value may be silently ignored in the future.
2016-11-09 14:31:48.774 1082 INFO keystone.cmd.cli [-] Created domain default
2016-11-09 14:31:48.802 1082 INFO keystone.cmd.cli [req-ace08b7c-d0d2-4b18-b792-1ec3402575b1 - - - - -] Created project admin
"""


def test_keystone_log():
    log = KeystoneLog(context_wrap(KEYSTONE_LOG))
    assert len(log.get('INFO')) == 2
    assert len(list(log.get_after(datetime(2016, 11, 9, 14, 31, 0)))) == 4
