from insights.parsers import nova_user_ids
from insights.parsers import SkipException
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

    # 'nova' user not found
    with pytest.raises(SkipException) as ex:
        nova_user_ids.NovaUID(context_wrap(NOVA_USER_NOT_FOUND))
    assert '' in str(ex)

    # Blank input
    with pytest.raises(SkipException) as ex:
        nova_user_ids.NovaUID(context_wrap(EMPTY_CONTENT))
    assert '' in str(ex)

    # Any other output. This is not expected
    nova_uid = nova_user_ids.NovaUID(context_wrap(NOVA_UID + '\n' + NOVA_UID))
    assert nova_uid.data is None


def test_nova_migration_uid():
    nova_migration_uid = nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID))
    assert nova_migration_uid.data == 153

    # 'nova_migration' user not found
    with pytest.raises(SkipException) as ex:
        nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_USER_NOT_FOUND))
    assert '' in str(ex)

    # Blank input
    with pytest.raises(SkipException) as ex:
        nova_user_ids.NovaMigrationUID(context_wrap(EMPTY_CONTENT))
    assert '' in str(ex)

    # Any other output. This is not expected
    nova_migration_uid = nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID + '\n' + NOVA_MIGRATION_UID))
    assert nova_migration_uid.data is None


def test_doc_examples():
    failed, total = doctest.testmod(
        nova_user_ids,
        globs={'nova_uid': nova_user_ids.NovaUID(context_wrap(NOVA_UID)),
               'nova_migration_uid': nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID))}
    )
    assert failed == 0
