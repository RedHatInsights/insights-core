from ...parsers import foreman_rake_db_migrate_status, ParseException
from ...tests import context_wrap
import doctest
import pytest


foreman_rake_db_migrate_status_doc_example = '''
database: foreman

 Status   Migration ID    Migration Name
--------------------------------------------------
   up     20090714132448  Create hosts
   up     20090714132449  Add audits table
   up     20090715143858  Create architectures
   up     20090717025820  Create media
   up     20090718060746  Create domains
   up     20090718064254  Create subnets
   up     20090720134126  Create operatingsystems
   up     20090722140138  Create models
'''

parser = foreman_rake_db_migrate_status.Sat6DBMigrateStatus


def test_FRDMS_doc_examples():
    status = parser(context_wrap(foreman_rake_db_migrate_status_doc_example))
    globs = {
        'Sat6DBMigrateStatus': parser,
        'shared': {parser: status},
        'status': status
    }
    failed, tested = doctest.testmod(foreman_rake_db_migrate_status, globs=globs)
    assert failed == 0


foreman_rake_db_migrate_status_made_up = '''

database: foreman

 Status   Migration ID    Migration Name
--------------------------------------------------
   up     20090714132448  Create hosts
   up     20090714132449  Add audits table
   up     20090715143858  Create architectures
   up     20090717025820  Create media
   up     20090718060746  Create domains
   up     20090718064254  Create subnets
   up     20090720134126  Create operatingsystems
 failed   20090722140138  Create models

'''


def test_FRDMS():
    status = parser(context_wrap(foreman_rake_db_migrate_status_made_up))
    assert status
    assert hasattr(status, 'database')
    assert hasattr(status, 'migrations')
    assert hasattr(status, 'up')
    assert hasattr(status, 'down')

    assert status.database == 'foreman'
    assert len(status.migrations) == 8
    assert '20090714132448' in status.migrations
    assert '20090722140138' in status.migrations
    assert '20090722140137' not in status.migrations
    assert 'up' not in status.migrations

    mig1 = foreman_rake_db_migrate_status.Migration('up', '20090714132448', 'Create hosts')
    assert status.migrations['20090714132448'] == mig1
    mig8 = foreman_rake_db_migrate_status.Migration('failed', '20090722140138', 'Create models')
    assert status.migrations['20090722140138'] == mig8

    assert len(status.up) == 7
    assert status.up[0] == mig1
    assert len(status.down) == 1
    assert status.down[0] == mig8


def test_FRDMS_parse_exception():
    with pytest.raises(ParseException) as exc:
        status = parser(context_wrap(''))
        assert not status
    assert 'Could not find database name nor any migrations' in str(exc)
