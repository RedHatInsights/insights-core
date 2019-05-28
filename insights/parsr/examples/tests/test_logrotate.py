from insights.parsr.examples.logrotate_conf import loads

EXAMPLE = """
# sample logrotate configuration file
compress

/var/log/messages {
    rotate 5
    weekly
    postrotate
        /usr/bin/killall -HUP syslogd
    endscript
}

"/var/log/httpd/access.log" /var/log/httpd/error.log {
    rotate 5
    mail www@my.org
    size 100k
    sharedscripts
    postrotate
        /usr/bin/killall -HUP httpd
    endscript
}

/var/log/news/* {
    monthly
    rotate 2
    olddir /var/log/news/old
    missingok
    postrotate
        kill -HUP 'cat /var/run/inn.pid'
    endscript
    nocompress
}
""".strip()


SIMPLE = """
# sample logrotate configuration file
compress

 /var/log/messages {
    rotate 5
    weekly
    postrotate
        /usr/bin/killall -HUP syslogd
    endscript
}
"""


def test_logrotate_simple():
    res = loads(SIMPLE)
    assert "compress" in res
    assert "/var/log/messages" in res


def test_logrotate_example():
    res = loads(EXAMPLE)
    assert res["compress"].value is None
    assert res["/var/log/messages"]["rotate"].value == 5
    assert res["/var/log/messages"]["rotate"][0].lineno == 5
    assert res["/var/log/messages"]["weekly"].value is None
    assert res["/var/log/messages"]["postrotate"].value == "/usr/bin/killall -HUP syslogd"
    assert res["/var/log/news/*"][0].lineno == 22


def xtest_logrotate_multikey():
    res = loads(EXAMPLE)
    assert res["compress"].value is None
    assert res["/var/log/httpd/access.log"]["rotate"].value == 5
    assert res["/var/log/httpd/access.log"]["size"].value == "100k"
    assert res["/var/log/httpd/access.log"]["sharedscripts"].value is None

    assert res["/var/log/httpd/error.log"]["rotate"].value == 5
    assert res["/var/log/httpd/error.log"]["size"].value == "100k"
    assert res["/var/log/httpd/error.log"]["sharedscripts"].value is None
    assert res["/var/log/news/*"]["postrotate"].value == "kill -HUP 'cat /var/run/inn.pid'"
