import doctest

from insights.parsers.cron_jobs import CronForeman
from insights.parsers import cron_jobs
from insights.tests import context_wrap


CRON_FOREMAN_SAMPLE1 = """
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

RAILS_ENV=production
FOREMAN_HOME=/usr/share/foreman

# Clean up the session entries in the database
15 23 * * *     foreman    /usr/sbin/foreman-rake db:sessions:clear 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

# Send out recurring notifications
0 7 * * *       foreman    /usr/sbin/foreman-rake reports:daily 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
0 5 * * 0       foreman    /usr/sbin/foreman-rake reports:weekly 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
0 3 1 * *       foreman    /usr/sbin/foreman-rake reports:monthly 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

# Expire old reports
30 7 * * *      foreman    /usr/sbin/foreman-rake reports:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
30 7 * * *      foreman    /usr/sbin/foreman-rake reports:expire days=3 report_type=ForemanOpenscap::ArfReport 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

# Expire old audits
0 1 * * *      foreman    /usr/sbin/foreman-rake audits:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/audit.log
"""


def test_doc():
    CronForeman.collect('test_reports_expire', lambda n: n if "foreman-rake reports:expire" in n else "")
    CronForeman.any('test_reports_expire_2', lambda n: n if "foreman-rake reports:expire" in n else "")
    env = {
        'foreman_cron': CronForeman(context_wrap(CRON_FOREMAN_SAMPLE1))
    }
    failed, total = doctest.testmod(cron_jobs, globs=env)
    assert failed == 0


def test_cron_foreman():
    CronForeman.collect('test_audit_expire', lambda n: n if "foreman-rake audits:expire" in n else "")
    cron_foreman = CronForeman(context_wrap(CRON_FOREMAN_SAMPLE1))
    assert len(cron_foreman.test_audit_expire) == 1
    assert '/var/log/foreman/audit.log' in cron_foreman.test_audit_expire[0]
