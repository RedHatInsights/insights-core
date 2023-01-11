import doctest
import pytest

from insights.core.exceptions import ParseException
from insights.parsers import cron_jobs
from insights.parsers.cron_jobs import CronFile, CronForeman
from insights.tests import context_wrap

CRON_FILE_SAMPLE1 = """
SHELL=/bin/sh
TEST_HOME=/usr/share/test

15 23 * * *     test    /usr/sbin/testaa 2>&1 >> /var/log/test.log
0 7 * * *       test    /usr/sbin/testbb 2>&1 >> /var/log/test.log
"""

CRON_FILE_SAMPLE2 = """
SHELL=/bin/sh
TEST_HOME=/usr/share/test

testinvliadline
15 23 * * *     test    /usr/sbin/testaa 2>&1 >> /var/log/test.log
@daily       test    /usr/sbin/testbb 2>&1 >> /var/log/test.log
30 7 * * *      test    /usr/sbin/testcc 2>&1 >> /var/log/test.log
30 8 * * *      user1    /usr/sbin/someone 2>&1 >> /var/log/user.log
30 9 * * *      user1    /usr/sbin/sometwo 2>&1 >> /var/log/user.log
30 10 * * *     user1    /usr/sbin/somethree 2>&1 >> /var/log/user.log
30 11 * * *      user1    /usr/sbin/somefour 2>&1 >> /var/log/user.log
@reboot     user1    /usr/sbin/somefive
"""

CRON_FILE_SAMPLE3 = """
SHELL=/bin/sh
TEST_HOME=/usr/share/test

testinvliadline
15 23 * * *     test    /usr/sbin/testaa 2>&1 >> /var/log/test.log
@wrongnickname       test    /usr/sbin/testbb 2>&1 >> /var/log/test.log
30 7 * * *      test    /usr/sbin/testcc 2>&1 >> /var/log/test.log
@reboot     test    /usr/sbin/testdd 2>&1 >> /var/log/test.log
"""

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
        'cron_obj': CronFile(context_wrap(CRON_FILE_SAMPLE1)),
        'foreman_jobs': CronForeman(context_wrap(CRON_FOREMAN_SAMPLE1))
    }
    failed, total = doctest.testmod(cron_jobs, globs=env)
    assert failed == 0


def test_cron_file():
    cron_obj = CronFile(context_wrap(CRON_FILE_SAMPLE2))
    assert len(cron_obj.jobs) == 8
    assert len(cron_obj.invalid_lines) == 1
    assert len(cron_obj.environment) == 2
    user1_jobs = cron_obj.search(username='user1')
    assert len(user1_jobs) == 5
    assert user1_jobs[-1].get('time') == '@reboot'
    assert user1_jobs[-1].get('command') == '/usr/sbin/somefive'
    assert user1_jobs[-1].get('raw') == '@reboot     user1    /usr/sbin/somefive'
    test_jobs = cron_obj.search(command__contains='test')
    assert len(test_jobs) == 3
    assert test_jobs[1].get('minute') == '0'
    assert test_jobs[1].get('hour') == '0'
    assert '/usr/sbin/testbb' in test_jobs[1].get('command')


def test_cron_file_except():
    with pytest.raises(ParseException):
        CronForeman(context_wrap(CRON_FILE_SAMPLE3))


def test_cron_foreman():
    cron_foreman = CronForeman(context_wrap(CRON_FOREMAN_SAMPLE2))
    assert len(cron_foreman.jobs) == 3
    assert len(cron_foreman.invalid_lines) == 1
    assert len(cron_foreman.environment) == 2

    assert 'SHELL' in cron_foreman.environment
    assert cron_foreman.environment.get('SHELL') == '/bin/sh'

    assert 'testinvaludline' in cron_foreman.invalid_lines[0]

    assert 'reports:expire' in cron_foreman.jobs[1].get('command')
    assert cron_foreman.jobs[1]['minute'] == '0'
    assert cron_foreman.jobs[1]['hour'] == '0'

    assert 'time' in cron_foreman.jobs[2]
    assert '@reboot' == cron_foreman.jobs[2].get('time')
