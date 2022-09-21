import doctest
import pytest

from insights.parsers.cron_jobs import CronForeman
from insights.parsers import ParseException, cron_jobs
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


CRON_FOREMAN_SAMPLE2 = """
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
testinvaludline

# Clean up the session entries in the database
15 23 * * *     foreman    /usr/sbin/foreman-rake db:sessions:clear 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
@daily foreman /usr/sbin/foreman-rake reports:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
@reboot foreman /usr/sbin/foreman-rake reports:clean
"""

CRON_FOREMAN_SAMPLE3 = """
SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

RAILS_ENV=production
FOREMAN_HOME=/usr/share/foreman
testinvaludline

# Clean up the session entries in the database
15 23 * * *     foreman    /usr/sbin/foreman-rake db:sessions:clear 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log

@tenyearly foreman /usr/sbin/foreman-rake reports:expire 2>&1 | gawk '{ print strftime("[\%Y-\%m-\%d \%H:\%M:\%S]"), $0 }' >>/var/log/foreman/cron.log
"""


def test_doc():
    env = {
        'foreman_jobs': CronForeman(context_wrap(CRON_FOREMAN_SAMPLE1))
    }
    failed, total = doctest.testmod(cron_jobs, globs=env)
    assert failed == 0


def test_cron_foreman():
    cron_foreman = CronForeman(context_wrap(CRON_FOREMAN_SAMPLE2))
    assert len(cron_foreman) == 3
    assert len(cron_foreman.invalid_lines) == 1
    assert len(cron_foreman.environment) == 2

    assert 'SHELL' in cron_foreman.environment
    assert cron_foreman.environment.get('SHELL') == '/bin/sh'

    assert 'testinvaludline' in cron_foreman.invalid_lines[0]

    assert 'reports:expire' in cron_foreman[1].get('command')
    assert cron_foreman[1]['minute'] == '0'
    assert cron_foreman[1]['hour'] == '0'
    assert len(cron_foreman.invalid_lines) == 1

    assert 'time' in cron_foreman[2]
    assert '@reboot' == cron_foreman[2].get('time')

    foreman_rake_lines = cron_foreman.search('foreman-rake')
    assert len(foreman_rake_lines) == 3
    assert 'foreman-rake reports:expire' in foreman_rake_lines[1].get('command')
    assert foreman_rake_lines[2].get('command') == '/usr/sbin/foreman-rake reports:clean'


def test_cron_foreman_except():
    with pytest.raises(ParseException):
        CronForeman(context_wrap(CRON_FOREMAN_SAMPLE3))
