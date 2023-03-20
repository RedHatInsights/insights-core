import doctest
from insights.parsers import semanage
from insights.tests import context_wrap

USERS_COUNT_OUTPUT_1 = """
{
    "staff_u": 2
}
""".strip()

USERS_COUNT_OUTPUT_2 = """
{
    "staff_u": 2,
    "test_u": 4
}
""".strip()


def test_docs():
    users = semanage.LinuxUserCountMapSelinuxUser(context_wrap(USERS_COUNT_OUTPUT_1))
    env = {'users': users}
    failed, total = doctest.testmod(semanage, globs=env)
    assert failed == 0


def test_users_count_map_staffu_selinux_user():
    users = semanage.LinuxUserCountMapSelinuxUser(context_wrap(USERS_COUNT_OUTPUT_2))
    assert 'staff_u' in users
    assert users['staff_u'] == 2
    assert 'test_u' in users
    assert users['test_u'] == 4
