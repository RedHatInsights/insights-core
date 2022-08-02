import doctest

from insights.parsers import system_user_dirs
from insights.parsers.system_user_dirs import SystemUserDirs
from insights.tests import context_wrap

PACKAGES = ["ca-certificates", "kmod", "sssd-ldap"]


def test_system_user_dirs():
    test = SystemUserDirs(context_wrap(PACKAGES))
    assert test.packages == PACKAGES


def test_doc_examples():
    env = {
        "system_user_dirs": SystemUserDirs(context_wrap(PACKAGES))
    }
    failed, total = doctest.testmod(system_user_dirs, globs=env)
    assert failed == 0
