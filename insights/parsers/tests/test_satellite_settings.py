import doctest
import pytest

from insights.parsers import (
    satellite_settings, SkipException, ParseException)
from insights.core.plugins import ContentException
from insights.tests import context_wrap


SATELLITE_SETTINGS_1 = '''
           name            | value |  default
---------------------------+-------+-----------
 unregister_delete_host    |       | --- false+
                           |       | ...
 destroy_vm_on_host_delete |       | --- true +
                           |       | ...
(2 rows)

'''

SATELLITE_SETTINGS_2 = '''
        name            |  value   |  default
---------------------------+----------+-----------
unregister_delete_host    | --- true+| --- false+
                        | ...      | ...
destroy_vm_on_host_delete |          | --- true +
                        |          | ...
(2 rows)
'''

SATELLITE_SETTINGS_3 = '''
           name            | value |  default
---------------------------+-------+-----------
(0 rows)

'''

SATELLITE_SETTINGS_BAD_4 = '''
           name            | value |  default
---------------------------+-------+-----------
unregister_delete_host    | --- true+| --- false+ |
                        | ...      | ...
destroy_vm_on_host_delete |          | --- true + |
                        |          | ...
(2 rows)

'''

SATELLITE_SETTINGS_BAD_5 = '''
        name            |  value   |  default
---------------------------+----------+-----------
unregister_delete_host    | | --- false+
                        |    | a: b: 3+
                        |           |...
destroy_vm_on_host_delete |          | --- true +
                        |          | ...
(2 rows)
'''


SATELLITE_SETTINGS_WRONG_1 = '''
-bash: psql: command not found
'''

SATELLITE_SETTINGS_WRONG_2 = '''
su: user postgres does not exist
'''

SATELLITE_SETTINGS_WRONG_3 = '''
psql: FATAL:  database "foreman" does not exist
'''


def test_HTL_doc_examples():
    settings = satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_2))
    globs = {
        'settings': settings
    }
    failed, tested = doctest.testmod(satellite_settings, globs=globs)
    assert failed == 0


def test_no_value():
    settings = satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_1))
    assert(len(settings)) == 2
    assert not settings['unregister_delete_host']
    assert settings['destroy_vm_on_host_delete']


def test_exception():
    with pytest.raises(ContentException):
        satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_WRONG_1))
    with pytest.raises(SkipException):
        satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_WRONG_2))
    with pytest.raises(SkipException):
        satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_WRONG_3))
    with pytest.raises(SkipException):
        satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_3))
    with pytest.raises(SkipException):
        satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_BAD_4))
    with pytest.raises(ParseException):
        satellite_settings.SatelliteSettings(context_wrap(SATELLITE_SETTINGS_BAD_5))
