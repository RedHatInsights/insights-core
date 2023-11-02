from insights.parsers import squid
from insights.tests import context_wrap

SQUID_CACHE_LOG = """
2023/11/01 06:00:33 kid1|   Took 0.00 seconds (  0.00 entries/sec).
FATAL: Couldn't start logfile helper
Squid Cache (Version 3.5.20): Terminated abnormally.
CPU Usage: 0.046 seconds = 0.033 user + 0.013 sys
Maximum Resident Size: 34784 KB
Page faults with physical i/o: 0
2023/11/01 06:01:16 kid1| Set Current Directory to /var/spool/squid
2023/11/01 06:01:16 kid1| Starting Squid Cache version 3.5.20 for x86_64-redhat-linux-gnu...
2023/11/01 06:01:16 kid1| Service Name: squid
""".strip()


def test_doc():
    """
    To make the examples readable, it's better to show one of the main usage "last_scan".
    And the last_scan should be called before the parser initialation.
    However, the initialization is done here, so the "last_scan" in the example won't work.
    As a result, it will rasise error when refering the result key.
    So we will not thest the examples, just show the users how to use it.
    """
    pass


def test_squid_cache_log():
    squid.SquidCacheLog.last_scan('start_error_test', 'Terminated abnormally')
    cache_log = squid.SquidCacheLog(context_wrap(SQUID_CACHE_LOG))
    assert cache_log.start_error_test
    assert cache_log.start_error_test.get('raw_message') == "Squid Cache (Version 3.5.20): Terminated abnormally."
