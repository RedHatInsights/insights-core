import doctest
import pytest
from insights.core.dr import SkipComponent
from insights.parsers import semanage
from insights.tests import context_wrap

USERS_COUNT_OUTPUT_1 = """
2
""".strip()

USERS_COUNT_OUTPUT_2 = """
3
4
""".strip()


def test_docs():
    users = semanage.UsersCountMapStaffuSelinuxUser(context_wrap(USERS_COUNT_OUTPUT_1))
    env = {'users': users}
    failed, total = doctest.testmod(semanage, globs=env)
    assert failed == 0


def test_users_count_map_staffu_selinux_user():
    users = semanage.UsersCountMapStaffuSelinuxUser(context_wrap(USERS_COUNT_OUTPUT_1))
    assert users.count == 2


def test_users_count_map_staffu_selinux_user_except():
    with pytest.raises(SkipComponent):
        semanage.UsersCountMapStaffuSelinuxUser(context_wrap(USERS_COUNT_OUTPUT_2))
