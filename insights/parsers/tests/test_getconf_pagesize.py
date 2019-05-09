from insights.parsers.getconf_pagesize import GetconfPageSize
from insights.tests import context_wrap

GETCONFPAGESIZE1 = """
4096
""".strip()

GETCONFPAGESIZE2 = """
16384
""".strip()


class Testgetconfpagesize():
    def test_getconf_PAGESIZE1(self):
        result = GetconfPageSize(context_wrap(GETCONFPAGESIZE1))
        assert result.page_size == 4096

    def test_getconf_PAGESIZE2(self):
        result = GetconfPageSize(context_wrap(GETCONFPAGESIZE2))
        assert result.page_size == 16384
