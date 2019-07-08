from insights.parsers.getconf_pagesize import GetconfPageSize
from insights.tests import context_wrap
from insights.parsers import getconf_pagesize
import doctest

GETCONFPAGESIZE1 = """
4096
""".strip()

GETCONFPAGESIZE2 = """
16384
""".strip()


def test_getconf_PAGESIZE1():
    result = GetconfPageSize(context_wrap(GETCONFPAGESIZE1))
    assert result.page_size == 4096


def test_getconf_PAGESIZE2():
    result = GetconfPageSize(context_wrap(GETCONFPAGESIZE2))
    assert result.page_size == 16384


def test_doc():
    env = {
            "pagesize_parsed": GetconfPageSize(context_wrap(GETCONFPAGESIZE1))
    }
    print(env)
    failed, total = doctest.testmod(getconf_pagesize, globs=env)
    assert failed == 0
