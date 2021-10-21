from insights.parsers import logrotate_conf
from insights.parsers.logrotate_conf import LogrotateConf
from insights.tests import context_wrap
import doctest

LOGROTATE_CONF_1 = """
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
    monthly
    create 0664 root utmp
        minsize 1M
    rotate 1
}
""".strip()

LOGROTATE_CONF_2 = """
#1343753: cant use * here cause not all logs in this folder will be owned by tomcat
/var/log/candlepin/access.log /var/log/candlepin/audit.log /var/log/candlepin/candlepin.log /var/log/candlepin/error.log {
# logrotate 3.8 requires the su directive,
# where as prior versions do not recognize it.
#LOGROTATE-3.8#    su tomcat tomcat
    copytruncate
    daily
    rotate 52
    compress
    missingok
    create 0644 tomcat tomcat
}
""".strip()

LOGROTATE_CONF_3 = """
/var/log/cron
/var/log/maillog
/var/log/messages
/var/log/secure
/var/log/spooler
{
    sharedscripts
    postrotate
        /bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null || true
    endscript
}
""".strip()

LOGROTATE_MAN_PAGE_DOC = """
# sample file
compress

/var/log/messages {
    rotate 5
    weekly
    postrotate
                /sbin/killall -HUP syslogd
    endscript
}

"/var/log/httpd/access.log" /var/log/httpd/error.log {
    rotate 5
    mail www@my.org
    size=100k
    sharedscripts
    postrotate
                /sbin/killall -HUP httpd
    endscript
}

/var/log/news/news.crit
/var/log/news/olds.crit  {
    monthly
    rotate 2
    olddir /var/log/news/old
    missingok
    postrotate
                kill -HUP `cat /var/run/inn.pid`
    endscript
    nocompress
}
""".strip()


LOGROTATE_CONF_4 = """
/var/log/news/olds.crit  {
    monthly
    rotate 2
    olddir /var/log/news/old
    missingok
    prerotate
        export LANG=C
        ACTLOG_RLOG=/var/log/actlog/selfinfo/postrotate
        {
                E=/var/log/actlog.exports/eventlog.1
                C=/var/log/actlog.exports/cpuload.1
                if [ -e ${C}.gz -a -e $E ] ; then
                        E_backup=eventlog.1-`date -r $E +%F.%H%M%S`
                        echo "WARNING: Both ${C}.gz and $E exist ; move eventlog.1 to sysinfo/${E_backup}"
                        mv -f $E /var/log/actlog/sysinfo/${E_backup}
                fi
        } >>${ACTLOG_RLOG} 2>&1
        exit 0
  endscript
    nocompress
}
""".strip()


def test_web_xml_doc_examples():
    env = {
        'log_rt': logrotate_conf.LogrotateConf(context_wrap(LOGROTATE_MAN_PAGE_DOC, path='/etc/logrotate.conf')),
        'log_rt_peg': logrotate_conf.LogRotateConfPEG(context_wrap(LOGROTATE_MAN_PAGE_DOC, path='/etc/logrotate.conf')),
    }
    failed, total = doctest.testmod(logrotate_conf, globs=env)
    assert failed == 0


def test_logrotate_conf_1():
    log_rt = LogrotateConf(context_wrap(LOGROTATE_CONF_1, path='/etc/logrotate.conf'))
    assert 'compress' not in log_rt.options
    assert log_rt['include'] == '/etc/logrotate.d'
    assert log_rt['/var/log/wtmp']['minsize'] == '1M'
    assert log_rt.log_files == ['/var/log/wtmp']
    assert log_rt['/var/log/wtmp']['create'] == '0664 root utmp'


def test_logrotate_conf_2():
    log_rt = LogrotateConf(context_wrap(LOGROTATE_CONF_2, path='/etc/logrotate.conf'))
    assert log_rt.options == []
    assert '/var/log/candlepin/access.log' in log_rt.log_files
    assert log_rt['/var/log/candlepin/access.log']['rotate'] == '52'
    assert log_rt['/var/log/candlepin/error.log']['missingok'] is True
    assert log_rt['/var/log/candlepin/audit.log']['create'] == '0644 tomcat tomcat'


def test_logrotate_conf_3():
    log_rt = LogrotateConf(context_wrap(LOGROTATE_CONF_3, path='/etc/logrotate.conf'))
    assert log_rt.options == []
    assert '/var/log/maillog' in log_rt.log_files
    assert log_rt['/var/log/cron']['sharedscripts'] is True
    assert log_rt['/var/log/messages']['postrotate'] == [
            '/bin/kill -HUP `cat /var/run/syslogd.pid 2> /dev/null` 2> /dev/null || true']


def test_logrotate_conf_4():
    log_rt = LogrotateConf(context_wrap(LOGROTATE_CONF_4, path='/etc/logrotate.d/abc'))
    assert '/var/log/news/olds.crit' in log_rt.log_files
    assert 'mv -f $E /var/log/actlog/sysinfo/${E_backup}' in log_rt['/var/log/news/olds.crit']['prerotate']
    assert '} >>${ACTLOG_RLOG} 2>&1' in log_rt['/var/log/news/olds.crit']['prerotate']
    assert len(log_rt['/var/log/news/olds.crit']['prerotate']) == 12
