import doctest
import pytest

from insights.core.exceptions import ContentException, ParseException, SkipComponent
from insights.parsers import satellite_content_hosts_count
from insights.tests import context_wrap


SATELLITE_CONTENT_HOSTS_COUNT = '''
 count
-------
    13
(1 row)

'''

SATELLITE_CONTENT_HOSTS_COUNT_WRONG_1 = '''
-bash: psql: command not found
'''

SATELLITE_CONTENT_HOSTS_COUNT_WRONG_2 = '''
su: user postgres does not exist
'''

SATELLITE_CONTENT_HOSTS_COUNT_WRONG_3 = '''
psql: FATAL:  database "foreman" does not exist
'''

SATELLITE_CONTENT_HOSTS_COUNT_WRONG_4 = '''
 count
-------
    abc
(1 row)

'''


def test_HTL_doc_examples():
    clients = satellite_content_hosts_count.SatelliteContentHostsCount(context_wrap(SATELLITE_CONTENT_HOSTS_COUNT))
    globs = {
        'clients': clients
    }
    failed, tested = doctest.testmod(satellite_content_hosts_count, globs=globs)
    assert failed == 0


def test_wrong_output():
    with pytest.raises(ContentException):
        satellite_content_hosts_count.SatelliteContentHostsCount(context_wrap(SATELLITE_CONTENT_HOSTS_COUNT_WRONG_1))
    with pytest.raises(SkipComponent):
        satellite_content_hosts_count.SatelliteContentHostsCount(context_wrap(SATELLITE_CONTENT_HOSTS_COUNT_WRONG_2))
    with pytest.raises(SkipComponent):
        satellite_content_hosts_count.SatelliteContentHostsCount(context_wrap(SATELLITE_CONTENT_HOSTS_COUNT_WRONG_3))
    with pytest.raises(ParseException):
        satellite_content_hosts_count.SatelliteContentHostsCount(context_wrap(SATELLITE_CONTENT_HOSTS_COUNT_WRONG_4))
