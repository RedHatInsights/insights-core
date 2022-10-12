import doctest
from insights.parsers import semanage
from insights.tests import context_wrap

SELINUX_LOGIN_OUTPUT_1 = """

Login Name           SELinux User         MLS/MCS Range        Service

__default__          unconfined_u         s0-s0:c0.c1023       *
root                 unconfined_u         s0-s0:c0.c1023       *
system_u             system_u             s0-s0:c0.c1023       *
"""

SELINUX_LOGIN_OUTPUT_2 = """

Login Name           SELinux User         MLS/MCS Range        Service

__default__          unconfined_u         s0-s0:c0.c1023       *
root                 unconfined_u         s0-s0:c0.c1023       *
testa                staff_u              s0-s0:c0.c1024       *
"""


def test_docs():
    users = semanage.SemanageLoginList(context_wrap(SELINUX_LOGIN_OUTPUT_1))
    env = {'users': users}
    failed, total = doctest.testmod(semanage, globs=env)
    assert failed == 0


def test_selinux_login():
    users = semanage.SemanageLoginList(context_wrap(SELINUX_LOGIN_OUTPUT_2))
    staff_u_users = users.search(selinux_user='staff_u')
    assert len(staff_u_users) == 1
    assert staff_u_users[0]['login_name'] == 'testa'
    assert staff_u_users[0]['mls_mcs_range'] == 's0-s0:c0.c1024'
    assert staff_u_users[0]['service'] == '*'
