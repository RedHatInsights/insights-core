import doctest

from insights.parsers import httpd_open_nfs
from insights.parsers.httpd_open_nfs import HttpdOnNFSFilesCount
from insights.tests.parsers import skip_exception_check
from insights.tests import context_wrap

http_nfs = """
{"http_ids": [1787, 2399], "nfs_mounts": ["/data", "/www"], "open_nfs_files": 1000}
""".strip()


def test_http_nfs():
    httpd_nfs_counting = HttpdOnNFSFilesCount(context_wrap(http_nfs))
    assert len(httpd_nfs_counting.data) == 3
    assert httpd_nfs_counting.http_ids == [1787, 2399]
    assert httpd_nfs_counting.nfs_mounts == ["/data", "/www"]
    assert httpd_nfs_counting.data.get("open_nfs_files") == 1000


def test_empty():
    assert 'Empty output.' in skip_exception_check(HttpdOnNFSFilesCount)


def test_http_nfs_documentation():
    env = {
        'httpon_nfs': HttpdOnNFSFilesCount(context_wrap(http_nfs))
    }
    failed, total = doctest.testmod(httpd_open_nfs, globs=env)
    assert failed == 0
