from insights.parsers.logrotate_conf import LogrotateConf
from insights.combiners import logrotate_conf
from insights.combiners.logrotate_conf import LogrotateConfAll
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
/var/log/candlepin/*.log {
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

LOGROTATE_CONF_NO_FILE = """
# use date as a suffix of the rotated file
dateext

# RPM packages drop log rotation information into this directory
include /etc/logrotate.d
""".strip()

LOGROTATE_MAN_PAGE_DOC_1 = """
# sample file
compress
rotate 7
include /etc/logrotate.d

/var/log/messages {
    rotate 5
    weekly
    postrotate
                /sbin/killall -HUP syslogd
    endscript
}
""".strip()

LOGROTATE_MAN_PAGE_DOC_2 = """
"/var/log/httpd/access.log" /var/log/httpd/error.log {
    rotate 5
    mail www@my.org
    size=100k
    sharedscripts
    postrotate
                /sbin/killall -HUP httpd
    endscript
}
""".strip()

LOGROTATE_MAN_PAGE_DOC_3 = """
/var/log/news/*.crit
{
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

LOGRT_CONF_NO_INCLUDE = """
copytruncate
weekly
rotate 4
create
dateext
""".strip()


def test_web_xml_doc_examples():
    env = {
            'all_lrt': LogrotateConfAll(
                [
                    LogrotateConf(context_wrap(LOGROTATE_MAN_PAGE_DOC_1, path='/etc/logrotate.conf')),
                    LogrotateConf(context_wrap(LOGROTATE_MAN_PAGE_DOC_2, path='/etc/logrotate.d/httpd')),
                    LogrotateConf(context_wrap(LOGROTATE_MAN_PAGE_DOC_3, path='/etc/logrotate.d/newscrit'))
                ])
          }
    failed, total = doctest.testmod(logrotate_conf, globs=env)
    assert failed == 0


def test_logrotate_conf_combiner():
    all_lrt = LogrotateConfAll(
            [
                LogrotateConf(context_wrap(LOGROTATE_CONF_1, path='/etc/logrotate.conf')),
                LogrotateConf(context_wrap(LOGROTATE_CONF_2, path='/etc/logrotate.d/candlepin')),
                LogrotateConf(context_wrap(LOGROTATE_CONF_3, path='/etc/logrotate.d/xx'))
            ])
    assert all_lrt.global_options == ['weekly', 'rotate', 'create', 'dateext', 'include']
    assert all_lrt['rotate'] == '4'
    assert '/var/log/httpd/access.log' not in all_lrt
    assert all_lrt['/var/log/httpd/access.log'] is None
    assert all_lrt.options_of_logfile('/var/log/httpd/access.log') is None
    assert all_lrt.configfile_of_logfile('/var/log/httpd/access.log') is None
    assert '/var/log/candlepin/error.log' in all_lrt
    assert all_lrt['/var/log/candlepin/candlepin.log']['rotate'] == '52'
    assert all_lrt.configfile_of_logfile('/var/log/wtmp') == '/etc/logrotate.conf'
    assert all_lrt.configfile_of_logfile('/var/log/candlepin/access.log') == '/etc/logrotate.d/candlepin'
    assert all_lrt.configfile_of_logfile('/var/log/maillog') == '/etc/logrotate.d/xx'
    assert all_lrt.options_of_logfile('/var/log/maillog')['sharedscripts'] is True


def test_logrotate_conf_combiner_no_logfile():
    all_lrt = LogrotateConfAll(
            [
                LogrotateConf(context_wrap(LOGROTATE_CONF_NO_FILE, path='/etc/logrotate.conf')),
            ])
    assert all_lrt.global_options == ['dateext', 'include']
    assert all_lrt.log_files == []
    assert all_lrt.options_of_logfile('/var/log/httpd/access.log') is None
    assert all_lrt.configfile_of_logfile('/var/log/httpd/access.log') is None


def test_logrotate_conf_combiner_configfile():
    all_lrt = LogrotateConfAll(
            [
                LogrotateConf(context_wrap(LOGROTATE_CONF_NO_FILE, path='/etc/logrotate.conf')),
                LogrotateConf(context_wrap(LOGROTATE_CONF_3, path='/etc/logrotate.d/xx'))
            ])
    assert '/var/log/btmp' not in all_lrt
    assert all_lrt.global_options == ['dateext', 'include']
    assert all_lrt.configfile_of_logfile('/var/log/messages') == '/etc/logrotate.d/xx'


def test_logrotate_conf_combiner_no_include():
    all_lrt = LogrotateConfAll(
            [
                LogrotateConf(context_wrap(LOGRT_CONF_NO_INCLUDE, path='/etc/logrotate.conf')),
                LogrotateConf(context_wrap(LOGROTATE_CONF_2, path='/etc/logrotate.d/candlepin')),
                LogrotateConf(context_wrap(LOGROTATE_CONF_3, path='/etc/logrotate.d/xx'))
            ])
    assert all_lrt.global_options == ['copytruncate', 'weekly', 'rotate', 'create', 'dateext']
    assert 'include' not in all_lrt.global_options
    assert '/var/log/messages' not in all_lrt
