import doctest

from insights.parsers import system_user_dirs
from insights.parsers.system_user_dirs import SystemUserDirs
from insights.tests import context_wrap

DATA = ["ca-certificates", "kmod", "sssd-ldap"]


def test_system_user_dirs():
    test = SystemUserDirs(context_wrap(DATA))
    assert test.data == DATA


def test_doc_examples():
    env = {
        "system_user_dirs": SystemUserDirs(context_wrap(DATA))
    }
    failed, total = doctest.testmod(system_user_dirs, globs=env)
    assert failed == 0
