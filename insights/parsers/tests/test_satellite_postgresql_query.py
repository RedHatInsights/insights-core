import doctest
import pytest

from insights.parsers import (
    satellite_postgresql_query, ParseException, SkipException)
from insights.core.plugins import ContentException
from insights.tests import context_wrap


SATELLITE_POSTGRESQL_WRONG_1 = '''
-bash: psql: command not found
'''

SATELLITE_POSTGRESQL_WRONG_2 = '''
su: user postgres does not exist
'''

SATELLITE_POSTGRESQL_WRONG_3 = '''
psql: FATAL:  database "foreman" does not exist
'''

SATELLITE_POSTGRESQL_WRONG_4 = '''
'''

SATELLITE_POSTGRESQL_WRONG_5 = '''
            name        |          type
------------------------+-------------------------
test_compute_resource1  | Foreman::Model::Libvirt
test_compute_resource2  | Foreman::Model::RHV
(abc rows)
'''

SATELLITE_POSTGRESQL_WRONG_6 = '''
            name        |          type
------------------------+-------------------------
test_compute_resource1  Foreman::Model::Libvirt
test_compute_resource2 | Foreman::Model::RHV
(2 rows)
'''

SATELLITE_POSTGRESQL_WRONG_7 = '''
            name        |          type
------------------------+-------------------------
test_compute_resource1  | Foreman::Model::Libvirt
test_compute_resource2  | Foreman::Model::RHV
(3 rows)
'''

SATELLITE_POSTGRESQL_NO_ROWS = '''
           name            | value |  default
---------------------------+-------+-----------
(0 rows)
'''

test_data_1 = '''
            name
---------------------------------
 fix_db_cache
 foreman_tasks_sync_task_timeout
 dynflow_enable_console
(3 rows)
'''

test_data_2 = '''
           col1            | col2  |  col3
---------------------------+-------+-----------
 unregister_delete_host    |       | --- false+
                           |       | ...
 destroy_vm_on_host_delete |       | --- true +
                           |       | ...
(2 rows)
'''

test_data_3 = '''
            name        |          type
------------------------+-------------------------
test_compute_resource1 | Foreman::Model::Libvirt
test_compute_resource2 | Foreman::Model::RHV
(2 rows)
'''

test_data_4 = '''
           col1            | col2  |  col3      | col4
---------------------------+-------+------------+-----
 unregister_delete_host    |  abc  | --- false+ | avalue
                           |  def  | ...        |
 destroy_vm_on_host_delete |  fss  | --- true + | bvalue
                           |  cdk  | ...        |
(2 rows)
'''

test_data_5 = '''
           name            |  value   |  default
---------------------------+----------+-----------
 unregister_delete_host    | --- true+| --- false+
                           | ...      | ...
 destroy_vm_on_host_delete |          | --- true +
                           |          | ...
 (2 rows)
'''

test_data_6 = '''
            name            |  url          |  value
 ---------------------------+---------------+-----------
    abc                     |               | --- false+
                            |               | ...
    def                     | http://xx.com | --- true +
                            |               | ...
    (2 rows)
'''

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
 unregister_delete_host    |       | --- false
 destroy_vm_on_host_delete |       | --- true
(2 rows)
'''

SATELLITE_SETTINGS_4 = '''
           name            | settings_type
---------------------------+---------------
 unregister_delete_host    | boolean
 destroy_vm_on_host_delete | boolean
(2 rows)
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


def test_satellite_postgesql_query_exception():
    with pytest.raises(ContentException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_1))
    with pytest.raises(SkipException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_2))
    with pytest.raises(SkipException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_3))
    with pytest.raises(SkipException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_4))
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_5))
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_6))
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_WRONG_7))
    with pytest.raises(SkipException):
        satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(SATELLITE_POSTGRESQL_NO_ROWS))
    with pytest.raises(ParseException):
        rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_3))
        rows.get_column_value('test_compute_resource1', 'type1')
    with pytest.raises(ParseException):
        rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_3))
        rows.get_column_value('test_compute_resource', 'type')


def test_satellite_postgesql_query():
    rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_1))
    assert len(rows) == 3
    assert 'fix_db_cache' in rows
    assert 'fix_db_cache1' not in rows
    assert sorted(rows[0].keys()) == ['name']
    assert rows[0]['name'] == 'fix_db_cache'
    assert rows[1]['name'] == 'foreman_tasks_sync_task_timeout'
    assert rows[2]['name'] == 'dynflow_enable_console'

    rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_2))
    assert len(rows) == 2
    assert sorted(rows[0].keys()) == ['col1', 'col2', 'col3']
    assert rows[0]['col1'] == 'unregister_delete_host'
    assert rows[0]['col2'] == []
    assert rows[0]['col3'] == ['--- false+', '...']
    assert rows[1]['col1'] == 'destroy_vm_on_host_delete'
    assert rows[1]['col2'] == []
    assert rows[1]['col3'] == ['--- true +', '...']
    assert rows.get_column_value('unregister_delete_host', 'col2') == ''
    assert rows.get_column_value('unregister_delete_host', 'col3') == ['--- false+', '...']

    rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_3))
    assert len(rows) == 2
    assert sorted(rows[0].keys()) == ['name', 'type']
    assert rows[0]['name'] == 'test_compute_resource1'
    assert rows[0]['type'] == ['Foreman::Model::Libvirt']
    assert rows[1]['name'] == 'test_compute_resource2'
    assert rows[1]['type'] == ['Foreman::Model::RHV']
    assert rows.get_column_value('test_compute_resource1', 'type') == 'Foreman::Model::Libvirt'

    rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_4))
    assert len(rows) == 2
    assert sorted(rows[0].keys()) == ['col1', 'col2', 'col3', 'col4']
    assert rows[0]['col1'] == 'unregister_delete_host'
    assert rows[0]['col2'] == ['abc', 'def']
    assert rows[0]['col3'] == ['--- false+', '...']
    assert rows[0]['col4'] == ['avalue']
    assert rows[1]['col1'] == 'destroy_vm_on_host_delete'
    assert rows[1]['col2'] == ['fss', 'cdk']
    assert rows[1]['col3'] == ['--- true +', '...']
    assert rows[1]['col4'] == ['bvalue']
    assert rows.get_column_value('unregister_delete_host', 'col2') == ['abc', 'def']
    assert rows.get_column_value('unregister_delete_host', 'col4') == 'avalue'


def test_HTL_doc_examples():
    query = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_6))
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_2))
    globs = {
        'query': query,
        'settings': settings
    }
    failed, tested = doctest.testmod(satellite_postgresql_query, globs=globs)
    assert failed == 0


def test_no_value():
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_1))
    assert(len(settings)) == 2
    assert not settings.get_settting('unregister_delete_host')
    assert settings.get_settting('destroy_vm_on_host_delete')

    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_3))
    assert(len(settings)) == 2
    assert not settings.get_settting('unregister_delete_host')
    assert settings.get_settting('destroy_vm_on_host_delete')

    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_4))
    assert(len(settings)) == 2
    assert settings.get_column_value('unregister_delete_host', 'settings_type') == 'boolean'
    with pytest.raises(ParseException):
        settings.get_settting('unregister_delete_host')


def test_exception():
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_BAD_4))
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_BAD_5))
