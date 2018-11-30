from insights.parsers import nova_user_ids
from insights.parsers import ParseException
from insights.tests import context_wrap

import doctest
import pytest


NOVA_UID = '''
162
'''.strip()

NOVA_USER_NOT_FOUND = '''
id: nova: no such user
'''.strip()

NOVA_MIGRATION_UID = '''
153
'''.strip()

NOVA_MIGRATION_USER_NOT_FOUND = '''
id: nova_migration: no such user
'''.strip()

EMPTY_CONTENT = '''
'''.strip()


def test_nova_uid():
    nova_uid = nova_user_ids.NovaUID(context_wrap(NOVA_UID))
    assert nova_uid.data == 162
    nova_user_not_found = nova_user_ids.NovaUID(context_wrap(NOVA_USER_NOT_FOUND))
    assert nova_user_not_found.data is None

    # Blank input
    ctx = context_wrap(EMPTY_CONTENT)
    with pytest.raises(ParseException) as ex:
        nova_user_ids.NovaUID(ctx)
    assert "Input content is empty." in str(ex)


def test_nova_migration_uid():
    nova_migration_uid = nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID))
    assert nova_migration_uid.data == 153
    nova_migration_user_not_found = nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_USER_NOT_FOUND))
    assert nova_migration_user_not_found.data is None

    # Blank input
    ctx = context_wrap(EMPTY_CONTENT)
    with pytest.raises(ParseException) as ex:
        nova_user_ids.NovaMigrationUID(ctx)
    assert "Input content is empty." in str(ex)


def test_doc_examples():
    failed, total = doctest.testmod(
        nova_user_ids,
        globs={'nova_uid': nova_user_ids.NovaUID(context_wrap(NOVA_UID)),
               'nova_user_not_found': nova_user_ids.NovaUID(context_wrap(NOVA_USER_NOT_FOUND)),
               'nova_migration_uid': nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID)),
               'nova_migration_user_not_found': nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_USER_NOT_FOUND))}
    )
    assert failed == 0
