from insights.parsers.httpd_limits import HttpdLimits
from insights.tests import context_wrap

HTTPD_LIMITS_ERR = """
cat: /proc/1100/limits: No such file or directory
""".strip()

HTTPD_LIMITS = """
Limit                     Soft Limit           Hard Limit           Units
Max cpu time              unlimited            unlimited            seconds
Max file size             unlimited            unlimited            bytes
Max data size             unlimited            unlimited            bytes
Max stack size            10485760             unlimited            bytes
Max core file size        0                    unlimited            bytes
Max resident set          unlimited            unlimited            bytes
Max processes             9                    99                   processes
Max open files            1024                 4096                 files
Max locked memory         65536                65536                bytes
Max address space         unlimited            unlimited            bytes
Max file locks            unlimited            unlimited            locks
Max pending signals       15211                15211                signals
Max msgqueue size         819200               819200               bytes
Max nice priority         0                    0
Max realtime priority     0                    0
Max realtime timeout      unlimited            unlimited            us
""".strip()


def test_httpd_limits():
    results = HttpdLimits(context_wrap(HTTPD_LIMITS))
    assert len(results) == 16
    results.max_processes = '99'
    for r in results:
        if 'Max cpu time' == r['Limit']:
            assert r['Hard_Limit'] == 'unlimited'
            assert r['Soft_Limit'] == 'unlimited'
        if 'Max realtime timeout' == r['Limit']:
            assert r['Units'] == 'us'


def test_httpd_limits_empty():
    results = HttpdLimits(context_wrap(HTTPD_LIMITS_ERR))
    assert len(results) == 0
