import doctest

from insights.parsers import cron_log
from insights.tests import context_wrap

CRON_LOG = """
Feb 19 03:49:01 smtcfc0247 CROND[899752]: (root) CMD (/etc/run /etc/cron/every15Minutes /var/venus/logs/cron/every15Minutes 5 4.4 >/dev/null 2>&1)
Feb 19 03:49:01 smtcfc0247 CROND[899751]: (root) CMD (/etc/run /etc/cron/everyHour /var/venus/logs/cron/everyHour 5 65.8 >/dev/null 2>&1)
Feb 19 03:49:01 smtcfc0247 CROND[899753]: (root) CMD (/etc/run /etc/cron/every5Minutes /var/venus/logs/cron/every5Minutes 5 43.0 >/dev/null 2>&1)
Feb 19 03:49:01 smtcfc0247 CROND[908273]: (root) CMD (run-parts /etc/cron.hourly)
""".strip()


def test_doc_examples():
    env = {
        'cron_log': cron_log.CronLog(context_wrap(CRON_LOG))
    }
    failed, total = doctest.testmod(cron_log, globs=env)
    assert failed == 0


def test_cron_log():
    logs = cron_log.CronLog(context_wrap(CRON_LOG))
    etc_run_cmds = logs.get('/etc/run')
    assert 3 == len(etc_run_cmds)
    assert etc_run_cmds[0].get('timestamp') == "Feb 19 03:49:01"
    assert etc_run_cmds[1].get('message') == "(root) CMD (/etc/run /etc/cron/everyHour /var/venus/logs/cron/everyHour 5 65.8 >/dev/null 2>&1)"
    assert etc_run_cmds[2].get('procname') == "CROND[899753]"
