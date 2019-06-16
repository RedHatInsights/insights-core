#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from insights.parsers import nova_user_ids
from insights.parsers import ParseException, SkipException
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

UNEXPECTED_OUTPUT = '''
foo
bar
9
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
        nova_user_ids.NovaUID(context_wrap(''))
    assert '' in str(ex)

    # Any other output. This is not expected
    with pytest.raises(ParseException) as ex:
        nova_user_ids.NovaUID(context_wrap(UNEXPECTED_OUTPUT))
    assert 'Unable to parse user ID' in str(ex)


def test_nova_migration_uid():
    nova_migration_uid = nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID))
    assert nova_migration_uid.data == 153

    # 'nova_migration' user not found
    with pytest.raises(SkipException) as ex:
        nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_USER_NOT_FOUND))
    assert '' in str(ex)

    # Blank input
    with pytest.raises(SkipException) as ex:
        nova_user_ids.NovaMigrationUID(context_wrap(''))
    assert '' in str(ex)

    # Any other output. This is not expected
    with pytest.raises(ParseException) as ex:
        nova_user_ids.NovaMigrationUID(context_wrap(UNEXPECTED_OUTPUT))
    assert 'Unable to parse user ID' in str(ex)


def test_doc_examples():
    failed, total = doctest.testmod(
        nova_user_ids,
        globs={'nova_uid': nova_user_ids.NovaUID(context_wrap(NOVA_UID)),
               'nova_migration_uid': nova_user_ids.NovaMigrationUID(context_wrap(NOVA_MIGRATION_UID))}
    )
    assert failed == 0
