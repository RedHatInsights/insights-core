import doctest
from insights import add_filter
from insights.specs import Specs
from insights.tests import context_wrap
from insights.parsers import cron_log
from insights.parsers.cron_log import CronLog

CRON_MSG_LOG = """
Feb 20 18:59:01 hostname CROND[14468]: (root) CMD (/usr/sbin/logrotate /etc/logrotate.d/redcloaklogs.conf)
Feb 20 19:00:01 hostname crond[14532]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
Feb 20 19:00:01 hostname crond[14532]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
Feb 20 19:01:01 hostname crond[14597]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
Feb 20 19:01:01 hostname crond[14597]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
Feb 20 19:01:01 hostname crond[14598]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
Feb 20 19:01:01 hostname crond[14598]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
Feb 20 19:02:01 hostname crond[14661]: (root) PAM ERROR (Authentication token is no longer valid; new one required)
Feb 20 19:02:01 hostname crond[14661]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)
""".strip()

add_filter(Specs.messages, [
    "CMD",
    "PAM",
    "FAILED"
])


def test_cron_log_messages():
    msg_info = CronLog(context_wrap(CRON_MSG_LOG))
    msg = msg_info.get("(root)")
    assert len(msg) == 9
    assert msg[0].get("timestamp") == "Feb 20 18:59:01"
    cron_log = msg_info.get("FAILED")
    assert len(cron_log) == 4
    assert cron_log[0].get("procname") == "crond[14532]"
    assert cron_log[0].get("message") == "(root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)"
    assert cron_log[0].get("raw_message") == "Feb 20 19:00:01 hostname crond[14532]: (root) FAILED to authorize user with PAM (Authentication token is no longer valid; new one required)"


def test_cron_messages_log_doc():
    env = {
            'cron_log_msg': cron_log.CronLog(context_wrap(CRON_MSG_LOG)),
          }
    failed, total = doctest.testmod(cron_log, globs=env)
    assert failed == 0
