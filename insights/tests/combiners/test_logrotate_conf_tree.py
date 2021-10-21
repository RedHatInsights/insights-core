# coding=utf-8
import pytest

from insights.combiners.logrotate_conf import LogRotateConfTree
from insights.parsers import logrotate_conf
from insights.parsr.query import first
from insights.tests import context_wrap


CONF = """
# see "man logrotate" for details
# rotate log files weekly
weekly

# keep 4 weeks worth of backlogs
rotate 4

# create new (empty) log files after rotating old ones
create

# use date as a suffix of the rotated file
dateext

# uncomment this if you want your log files compressed
#compress

# RPM packages drop log rotation information into this directory
include /etc/logrotate.d

# no packages own wtmp and btmp -- we'll rotate them here
/var/log/wtmp {
    missingok
    monthly
    create 0664 root utmp
    minsize 1M
    rotate 1
    postrotate
        do some stuff to wtmp
    endscript
}

/var/log/btmp {
    missingok
    monthly
    create 0600 root utmp
    postrotate
        do some stuff to btmp
    endscript
    rotate 1
}

# system-specific logs may be also be configured here.
""".strip()


JUNK_SPACE = """
#SEG_15.06.01 
/var/log/spooler
{
    compress
    missingok
    rotate 30
    size 1M
    sharedscripts
    postrotate
        /bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null || true
    endscript
}
""".strip()


LOGROTATE_MISSING_ENDSCRIPT = """
/var/log/example/*.log {
  daily
  missingok
  rotate 10
  dateext
  dateyesterday
  notifempty
  sharedscripts
  postrotate
    [ ! -f /var/run/openresty.pid ] || kill -USR1 `cat /var/run/example.pid`
    /usr/local/bin/mc cp $1 minio/matrix-prod-cluster/node1/example/
}
""".strip()


def test_logrotate_tree():
    p = logrotate_conf.LogRotateConfPEG(context_wrap(CONF, path="/etc/logrotate.conf"))
    conf = LogRotateConfTree([p])
    assert len(conf["weekly"]) == 1
    assert len(conf["/var/log/wtmp"]["missingok"]) == 1
    assert conf["/var/log/wtmp"]["postrotate"][first].value == "do some stuff to wtmp"

    assert len(conf["/var/log/btmp"]["rotate"]) == 1
    assert len(conf["/var/log/btmp"]["postrotate"]) == 1
    assert conf["/var/log/btmp"]["postrotate"][first].value == "do some stuff to btmp"


def test_junk_space():
    p = logrotate_conf.LogRotateConfPEG(context_wrap(JUNK_SPACE, path="/etc/logrotate.conf"))
    conf = LogRotateConfTree([p])
    assert "compress" in conf["/var/log/spooler"]


def test_logrotate_conf_combiner_missing_endscript():
    with pytest.raises(Exception):
        logrotate_conf.LogRotateConfPEG(context_wrap(LOGROTATE_MISSING_ENDSCRIPT, path='/etc/logrotate.conf')),
