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

SATELLITE_SETTINGS_5 = '''
           name            |  value   |  default  | settings_type
---------------------------+----------+-----------+---------------
 unregister_delete_host    | --- true+| --- false+| boolean
                           | ...      | ...       | 
 destroy_vm_on_host_delete |          | --- true +| boolean
                           |          | ...       | 
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


def test_get_column_exception():
    table = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_2))
    with pytest.raises(ParseException):
        table.get_column('col2', col1='unregister_delete_hostsfs')
    with pytest.raises(ParseException):
        table.get_column('col1', col2=[])
    with pytest.raises(ParseException):
        table.get_column('col5', col1='unregister_delete_host')


def test_satellite_postgesql_query():
    rows = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_1))
    assert len(rows) == 3
    assert sorted(rows[0].keys()) == ['name']
    assert rows[0]['name'] == 'fix_db_cache'
    assert rows[1]['name'] == 'foreman_tasks_sync_task_timeout'
    assert rows[2]['name'] == 'dynflow_enable_console'

    table = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_2))
    assert len(table) == 2
    assert sorted(table[0].keys()) == ['col1', 'col2', 'col3']
    assert table[0]['col1'] == 'unregister_delete_host'
    assert table[0]['col2'] == []
    assert table[0]['col3'] == ['--- false+', '...']
    assert table[1]['col1'] == 'destroy_vm_on_host_delete'
    assert table[1]['col2'] == []
    assert table[1]['col3'] == ['--- true +', '...']
    assert table.get_column('col2', col1='unregister_delete_host') == ''
    assert table.get_column('col3', col1='unregister_delete_host') == ['--- false+', '...']

    table = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_3))
    assert len(table) == 2
    assert sorted(table[0].keys()) == ['name', 'type']
    assert table[0]['name'] == 'test_compute_resource1'
    assert table[0]['type'] == ['Foreman::Model::Libvirt']
    assert table[1]['name'] == 'test_compute_resource2'
    assert table[1]['type'] == ['Foreman::Model::RHV']
    assert table.get_column('type', name='test_compute_resource1') == 'Foreman::Model::Libvirt'

    table = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_4))
    assert len(table) == 2
    assert sorted(table[0].keys()) == ['col1', 'col2', 'col3', 'col4']
    assert table[0]['col1'] == 'unregister_delete_host'
    assert table[0]['col2'] == ['abc', 'def']
    assert table[0]['col3'] == ['--- false+', '...']
    assert table[0]['col4'] == ['avalue']
    assert table[1]['col1'] == 'destroy_vm_on_host_delete'
    assert table[1]['col2'] == ['fss', 'cdk']
    assert table[1]['col3'] == ['--- true +', '...']
    assert table[1]['col4'] == ['bvalue']
    assert table.get_column('col2', col1='unregister_delete_host') == ['abc', 'def']
    assert table.get_column('col4', col1='unregister_delete_host') == 'avalue'


def test_HTL_doc_examples():
    query = satellite_postgresql_query.SatellitePostgreSQLQuery(context_wrap(test_data_6))
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_2))
    globs = {
        'query': query,
        'table': settings
    }
    failed, tested = doctest.testmod(satellite_postgresql_query, globs=globs)
    assert failed == 0


def test_no_value():
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_1))
    assert(len(settings)) == 2
    assert not settings.get_setting('unregister_delete_host')
    assert settings.get_setting('destroy_vm_on_host_delete')

    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_3))
    assert(len(settings)) == 2
    assert not settings.get_setting('unregister_delete_host')
    assert settings.get_setting('destroy_vm_on_host_delete')
    with pytest.raises(ParseException):
        settings.get_setting('non_existing_column')

    with pytest.raises(ParseException):
        settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_4))
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_3))
    settings = satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_5))
    assert settings.get_column('settings_type', name='unregister_delete_host') == 'boolean'


def test_exception():
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_BAD_4))
    with pytest.raises(ParseException):
        satellite_postgresql_query.SatelliteAdminSettings(context_wrap(SATELLITE_SETTINGS_BAD_5))
