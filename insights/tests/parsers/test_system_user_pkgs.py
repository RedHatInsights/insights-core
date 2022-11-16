import doctest

from insights.parsers import system_user_pkgs
from insights.parsers.system_user_pkgs import SystemUserPkgs
from insights.tests import context_wrap

PACKAGES = ["httpd-core"]


def test_system_user_dirs():
    test = SystemUserPkgs(context_wrap(PACKAGES))
    assert test.packages == PACKAGES


def test_doc_examples():
    env = {
        "system_user_pkgs": SystemUserPkgs(context_wrap(PACKAGES))
    }
    failed, total = doctest.testmod(system_user_pkgs, globs=env)
    assert failed == 0
