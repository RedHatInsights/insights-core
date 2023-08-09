import doctest
import pytest

from datetime import datetime

from insights.core.exceptions import SkipComponent
from insights.parsers import zdump_v
from insights.tests import context_wrap

NORMAL_OUTPUT = '''
/etc/localtime  -9223372036854689408 = NULL
/etc/localtime  Sun Mar 10 06:59:59 2019 UTC = Sun Mar 10 01:59:59 2019 EST isdst=0 gmtoff=-18000
/etc/localtime  Sun Mar 10 07:00:00 2019 UTC = Sun Mar 10 03:00:00 2019 EDT isdst=1 gmtoff=-14400
/etc/localtime  Sun Nov  3 05:59:59 2019 UTC = Sun Nov  3 01:59:59 2019 EDT isdst=1 gmtoff=-14400
/etc/localtime  Sun Nov  3 06:00:00 2019 UTC = Sun Nov  3 01:00:00 2019 EST isdst=0 gmtoff=-18000
/etc/localtime  Sun Mar 14 06:59:59 2038 UTC = Sun Mar 14 01:59:59 2038 EST isdst=0 gmtoff=-18000
/etc/localtime  Sun Mar 14 07:00:00 2038 UTC = Sun Mar 14 03:00:00 2038 EDT isdst=1 gmtoff=-14400
/etc/localtime  9223372036854775807 = NUL
'''.strip()

BAD_OUTPUT1 = ''

BAD_OUTPUT2 = '''
/etc/localtime  -9223372036854775808 = NULL
/etc/localtime  9223372036854689407 = NULL
'''.strip()

BAD_OUTPUT3 = '''
/etc/localtime  -9223372036854775808 = NULL
/etc/localtime  Sun Nov  3 06:00:00 2019 UTC = Sun Nov  3 01:00:00 2019 EST gmtoff=-18000
/etc/localtime  Sun Mar 14 06:59:59 2038 UTC = Sun Mar 14 01:59:59 2038 EST isdst=0
/etc/localtime  9223372036854689407 = NULL
'''.strip()


def test_doc_examples():
    env = {
        'zdump': zdump_v.ZdumpV(
            context_wrap(NORMAL_OUTPUT)),
    }
    failed, total = doctest.testmod(zdump_v, globs=env)
    assert failed == 0


def test_zdump_v():
    zdump = zdump_v.ZdumpV(context_wrap(NORMAL_OUTPUT))
    assert len(zdump) == 6
    assert zdump[0].get('utc_time') == datetime(2019, 3, 10, 6, 59, 59)
    assert zdump[0].get('utc_time_raw') == 'Sun Mar 10 06:59:59 2019 UTC'
    assert zdump[0].get('local_time') == datetime(2019, 3, 10, 1, 59, 59)
    assert zdump[0].get('local_time_raw') == 'Sun Mar 10 01:59:59 2019 EST'
    assert zdump[0].get('isdst') == 0
    assert zdump[0].get('gmtoff') == -18000
    assert zdump[1].get('utc_time') == datetime(2019, 3, 10, 7, 0, 0)
    assert zdump[1].get('utc_time_raw') == 'Sun Mar 10 07:00:00 2019 UTC'
    assert zdump[1].get('local_time') == datetime(2019, 3, 10, 3, 0, 0)
    assert zdump[1].get('local_time_raw') == 'Sun Mar 10 03:00:00 2019 EDT'
    assert zdump[1].get('isdst') == 1
    assert zdump[1].get('gmtoff') == -14400
    assert zdump[2].get('utc_time') == datetime(2019, 11, 3, 5, 59, 59)
    assert zdump[2].get('utc_time_raw') == 'Sun Nov  3 05:59:59 2019 UTC'
    assert zdump[2].get('local_time') == datetime(2019, 11, 3, 1, 59, 59)
    assert zdump[2].get('local_time_raw') == 'Sun Nov  3 01:59:59 2019 EDT'
    assert zdump[2].get('isdst') == 1
    assert zdump[2].get('gmtoff') == -14400
    assert zdump[3].get('utc_time') == datetime(2019, 11, 3, 6, 0, 0)
    assert zdump[3].get('utc_time_raw') == 'Sun Nov  3 06:00:00 2019 UTC'
    assert zdump[3].get('local_time') == datetime(2019, 11, 3, 1, 0, 0)
    assert zdump[3].get('local_time_raw') == 'Sun Nov  3 01:00:00 2019 EST'
    assert zdump[3].get('isdst') == 0
    assert zdump[3].get('gmtoff') == -18000
    assert zdump[4].get('utc_time') == datetime(2038, 3, 14, 6, 59, 59)
    assert zdump[4].get('utc_time_raw') == 'Sun Mar 14 06:59:59 2038 UTC'
    assert zdump[4].get('local_time') == datetime(2038, 3, 14, 1, 59, 59)
    assert zdump[4].get('local_time_raw') == 'Sun Mar 14 01:59:59 2038 EST'
    assert zdump[4].get('isdst') == 0
    assert zdump[4].get('gmtoff') == -18000
    assert zdump[5].get('utc_time') == datetime(2038, 3, 14, 7, 0, 0)
    assert zdump[5].get('utc_time_raw') == 'Sun Mar 14 07:00:00 2038 UTC'
    assert zdump[5].get('local_time') == datetime(2038, 3, 14, 3, 0, 0)
    assert zdump[5].get('local_time_raw') == 'Sun Mar 14 03:00:00 2038 EDT'
    assert zdump[5].get('isdst') == 1
    assert zdump[5].get('gmtoff') == -14400

    zdump = zdump_v.ZdumpV(context_wrap(BAD_OUTPUT2))
    assert len(zdump) == 0

    zdump = zdump_v.ZdumpV(context_wrap(BAD_OUTPUT3))
    assert len(zdump) == 1
    assert zdump[0].get('utc_time') == datetime(2038, 3, 14, 6, 59, 59)
    assert zdump[0].get('utc_time_raw') == 'Sun Mar 14 06:59:59 2038 UTC'
    assert zdump[0].get('local_time') == datetime(2038, 3, 14, 1, 59, 59)
    assert zdump[0].get('local_time_raw') == 'Sun Mar 14 01:59:59 2038 EST'
    assert zdump[0].get('isdst') == 0
    assert zdump[0].get('gmtoff') is None


def test_fail():
    with pytest.raises(SkipComponent) as e:
        zdump_v.ZdumpV(context_wrap(BAD_OUTPUT1))
    assert "No Data from command: /usr/sbin/zdump -v /etc/localtime -c 2019,2039" in str(e)
