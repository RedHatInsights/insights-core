import doctest
from insights.tests import context_wrap
from insights.combiners import du
from insights.parsers.du import DiskUsageDir

DISK_USAGE_DIR_SAMPLE1 = """
553500	/var/log
""".strip()

DISK_USAGE_DIR_SAMPLE2 = """
519228	/var/lib/pgsql
""".strip()


def test_disk_usage_dirs():
    parser1 = DiskUsageDir(context_wrap(DISK_USAGE_DIR_SAMPLE1))
    parser2 = DiskUsageDir(context_wrap(DISK_USAGE_DIR_SAMPLE2))
    disk_usage_dirs = du.DiskUsageDirs([parser1, parser2])
    assert disk_usage_dirs is not None
    assert set(disk_usage_dirs.keys()) == set(["/var/log", "/var/lib/pgsql"])
    assert disk_usage_dirs["/var/log"] == 553500
    assert disk_usage_dirs["/var/lib/pgsql"] == 519228


def test_disk_usage_dirs_docs():
    parser1 = DiskUsageDir(context_wrap(DISK_USAGE_DIR_SAMPLE1))
    parser2 = DiskUsageDir(context_wrap(DISK_USAGE_DIR_SAMPLE2))
    env = {'disk_usage_dirs': du.DiskUsageDirs([parser1, parser2])}
    failed, total = doctest.testmod(du, globs=env)
    assert failed == 0
