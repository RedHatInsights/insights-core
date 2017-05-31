import pytest
from insights.parsers.crontab import CrontabL, HeatCrontab, KeystoneCrontab, RootCrontab
from insights.tests import context_wrap

CRONTAB_DATA = """
# comment line
* * * * * /usr/bin/keystone-manage token_flush > /dev/null 2>&1
33 0 1 3 6 /bin/heat-manage purge_deleted -g days 7
* * * * * user_name /usr/local/bin/motd_update
"""

CRONTAB_BAD_DATA = """
# comment line
* * * * * /usr/bin/keystone-manage token_flush > /dev/null 2>&1
33 0 1 3 6 /bin/heat-manage purge_deleted -g days 7
* * * * * user_name /usr/local/bin/motd_update
Error reading crontab
"""


def crontab_tests(crontab_class):
    crontab = crontab_class(context_wrap(CRONTAB_DATA))
    assert crontab is not None
    assert [r.get('minute') for r in crontab] == ['*', '33', '*']
    assert crontab.search('heat-manage') == [
        {'minute': '33',
         'hour': '0',
         'day_of_month': '1',
         'month': '3',
         'day_of_week': '6',
         'command': '/bin/heat-manage purge_deleted -g days 7'}]
    assert crontab.search('crazy_123') == []
    assert crontab.search('motd')[0]['command'] == 'user_name /usr/local/bin/motd_update'

    with pytest.raises(AssertionError):
        crontab = crontab_class(context_wrap(CRONTAB_BAD_DATA))


def test_crontab():
    crontab_tests(CrontabL)


def test_heat_crontab():
    crontab_tests(HeatCrontab)


def test_keystone_crontab():
    crontab_tests(KeystoneCrontab)


def test_root_crontab():
    crontab_tests(RootCrontab)
