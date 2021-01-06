# -*- coding: UTF-8 -*-
from insights.core import LogFileOutput
from insights.parsers import ParseException
from insights.tests import context_wrap

from datetime import datetime
import pytest


class FakeMessagesClass(LogFileOutput):
    time_format = '%b %d %H:%M:%S'

    def bad_get_after(self, timestamp, lines=None):
        self.time_format = '%q/%1 %z:%v:%j'
        return super(FakeMessagesClass, self).get_after(timestamp, lines)

    def superget(self, s):
        for line in self.lines:
            if s in line:
                parts = line.split(None, 6)
                yield {
                    'timestamp': ' '.join(parts[0:3]),
                    'hostname': parts[3],
                    'service': parts[4][:-1],  # strip colon
                    'message': parts[5]
                }

    def listget(self, s):
        # Silly function to split lines containing s.
        for line in self.lines:
            if s in line:
                yield s.split(None, 6)


MESSAGES = """
Mar 27 03:18:15 system rsyslogd: [origin software="rsyslogd" swVersion="5.8.10" x-pid="1870" x-info="http://www.rsyslog.com"] first
Mar 27 03:18:16 system rsyslogd-2177: imuxsock lost 141 messages from pid 55082 due to rate-limiting
Mar 27 03:18:19 system rsyslogd-2177: imuxsock begins to drop messages from pid 55082 due to rate-limiting
Mar 27 03:18:21 system pulp: pulp.server.db.connection:INFO: Attempting Database connection with seeds = localhost:27017
Mar 27 03:18:21 system pulp: pulp.server.db.connection:INFO: Connection Arguments: {'max_pool_size': 10}
Mar 27 03:18:21 system pulp: pulp.server.db.connection:INFO: Database connection established with: seeds = localhost:27017, name = pulp_database
Mar 27 03:18:22 system rsyslogd-2177: imuxsock lost 145 messages from pid 55082 due to rate-limiting
Mar 27 03:18:24 system puppet-master[48226]: Setting manifest is deprecated in puppet.conf. See http://links.puppetlabs.com/env-settings-deprecations
Mar 27 03:18:24 system puppet-master[48226]:    (at /usr/lib/ruby/site_ruby/1.8/puppet/settings.rb:1095:in `issue_deprecations')
Mar 27 03:18:24 system puppet-master[48226]: Setting modulepath is deprecated in puppet.conf. See http://links.puppetlabs.com/env-settings-deprecations
Mar 27 03:18:24 system puppet-master[48226]:    (at /usr/lib/ruby/site_ruby/1.8/puppet/settings.rb:1095:in `issue_deprecations')
Mar 27 03:18:24 system puppet-master[48226]: Setting config_version is deprecated in puppet.conf. See http://links.puppetlabs.com/env-settings-deprecations
Mar 27 03:18:24 system puppet-master[48226]:    (at /usr/lib/ruby/site_ruby/1.8/puppet/settings.rb:1095:in `issue_deprecations')
Mar 27 03:18:25 system rsyslogd-2177: imuxsock begins to drop messages from pid 55082 due to rate-limiting
Mar 27 03:39:43 system pulp: pulp.server.webservices.middleware.exception:ERROR:   File "/usr/lib/python2.6/site-packages/web/application.py", line 230, in handle
     return self._delegate(fn, self.fvars, args)
   File "/usr/lib/python2.6/site-packages/web/application.py", line 405, in _delegate
     return handle_class(f)
   File "/usr/lib/python2.6/site-packages/web/application.py", line 396, in handle_class
     return tocall(*args)
   File "/usr/lib/python2.6/site-packages/pulp/server/webservices/controllers/decorators.py", line 227, in _auth_decorator
     value = method(self, *args, **kwargs)
   File "/usr/lib/python2.6/site-packages/pulp/server/webservices/controllers/consumers.py", line 503, in GET
     profile = manager.get_profile(consumer_id, content_type)
   File "/usr/lib/python2.6/site-packages/pulp/server/managers/consumer/profile.py", line 120, in get_profile
     raise MissingResource(profile_id=profile_id)
MissingResource: Missing resource(s): profile_id={'content_type': u'rpm', 'consumer_id': u'1786cd7f-2ab2-4212-9798-c0a454e97900'}
Mar 27 03:39:43 system rsyslogd-2177: imuxsock begins to drop messages from pid 55082 due to rate-limiting
Mar 27 03:39:46 system rsyslogd-2177: imuxsock lost 165 messages from pid 55082 due to rate-limiting
Mar 27 03:39:49 system rsyslogd-2177: imuxsock begins to drop messages from pid 55082 due to rate-limiting
Mar 27 03:49:10 system pulp: pulp.server.webservices.middleware.exception:ERROR: Missing resource(s): profile_id={'content_type': u'rpm', 'consumer_id': u'79d5aed1-5631-4f40-b970-585ee974eb87'}
"""


def test_messages_scanners():
    # Messages that are present can be kept
    FakeMessagesClass.keep_scan('puppet_master_logs', ' puppet-master')
    # Messages that are absent still turn up as an empty list
    FakeMessagesClass.keep_scan('kernel_logs', ' kernel')
    # Token scan of something that's present
    FakeMessagesClass.token_scan('middleware_exception_present', 'pulp.server.webservices.middleware.exception')
    # Token scan of something that's absent
    FakeMessagesClass.token_scan('cron_present', 'CRONTAB')

    # Check that duplicate scanners raise a value exception
    with pytest.raises(ValueError) as exc:
        FakeMessagesClass.keep_scan('kernel_logs', ' kernel')
    assert "'kernel_logs' is already a registered scanner key" in str(exc)

    def count_lost_messages(self):
        imuxsock_lines = 0
        lost_messages = 0
        for line in self.lines:
            if 'imuxsock lost' in line:
                parts = line.split(None)
                if parts[7].isdigit():
                    imuxsock_lines += 1
                    lost_messages += int(parts[7])
        return "lost {msgs} messages in {lines} lines".format(msgs=lost_messages, lines=imuxsock_lines)
    FakeMessagesClass.scan('lost_messages', count_lost_messages)

    ctx = context_wrap(MESSAGES, path='/var/log/messages')
    log = FakeMessagesClass(ctx)
    assert hasattr(log, 'puppet_master_logs')
    assert hasattr(log, 'kernel_logs')
    assert hasattr(log, 'middleware_exception_present')
    assert hasattr(log, 'cron_present')
    assert hasattr(log, 'lost_messages')

    assert len(log.puppet_master_logs) == 6
    assert log.puppet_master_logs[0]['raw_message'] == 'Mar 27 03:18:24 system puppet-master[48226]: Setting manifest is deprecated in puppet.conf. See http://links.puppetlabs.com/env-settings-deprecations'
    assert log.kernel_logs == []
    assert log.middleware_exception_present
    assert not log.cron_present
    assert log.lost_messages == 'lost 451 messages in 3 lines'


def test_messages_scanners_list():
    # Messages that are present can be kept
    FakeMessagesClass.keep_scan('puppet_master_manifest_logs', ['puppet-master', 'manifest'])
    FakeMessagesClass.keep_scan('puppet_master_first', ['puppet-master', 'first'])
    # Messages that are present can be kept for any of the list
    FakeMessagesClass.keep_scan('puppet_master_first_any', ['puppet-master', 'first'], check=any)
    FakeMessagesClass.keep_scan('puppet_master_first_any_3', ['puppet-master', 'first'], num=3, check=any)
    # Token scan of something that's absent
    FakeMessagesClass.token_scan('error_missing', ['ERROR', 'Missing'])
    # Token scan of something that's absent
    FakeMessagesClass.token_scan('error_info', ['ERROR', 'info'])
    # Token scan of something that's absent for any of the list
    FakeMessagesClass.token_scan('error_info_any', ['ERROR', 'info'], check=any)
    # Get the last line
    FakeMessagesClass.last_scan('puppet_master_manifest_last', ['puppet-master', 'manifest'])
    # Get the last line for any of the list
    FakeMessagesClass.last_scan('puppet_master_first_last_any', ['puppet-master', 'first'], check=any)

    ctx = context_wrap(MESSAGES, path='/var/log/messages')
    log = FakeMessagesClass(ctx)

    assert hasattr(log, 'puppet_master_manifest_logs')
    assert len(log.puppet_master_manifest_logs) == 1
    assert hasattr(log, 'error_missing')
    assert log.error_missing

    assert hasattr(log, 'puppet_master_first')
    assert len(log.puppet_master_first) == 0
    assert hasattr(log, 'error_info')
    assert log.error_info is False

    assert hasattr(log, 'puppet_master_first_any')
    assert len(log.puppet_master_first_any) == 7
    assert hasattr(log, 'puppet_master_first_any_3')
    assert len(log.puppet_master_first_any_3) == 3
    assert hasattr(log, 'error_info_any')
    assert log.error_info_any is True

    assert hasattr(log, 'puppet_master_manifest_last')
    assert 'puppet-master' in log.puppet_master_manifest_last['raw_message']
    assert 'manifest' in log.puppet_master_manifest_last['raw_message']
    assert hasattr(log, 'puppet_master_first_last_any')
    assert 'puppet-master' in log.puppet_master_first_last_any['raw_message']


def test_messages_get_after():
    ctx = context_wrap(MESSAGES, path='/var/log/messages')
    log = FakeMessagesClass(ctx)
    assert len(log.lines) == 31

    # Get lines after date
    # Remember, logs with no date are assumed to be in year we give it
    assert len(list(log.get_after(datetime(2017, 3, 27, 3, 39, 46)))) == 3
    # Get subset of lines after date
    pulp = log.get('pulp')  # includes /pulp/ in traceback
    assert len(pulp) == 8
    # Get lines after date, with one keyword
    after = list(log.get_after(datetime(2017, 3, 27, 3, 20, 30), 'pulp'))
    assert len(after) == 5
    # Get lines after date, with one keyword
    after = list(log.get_after(datetime(2017, 3, 27, 3, 40, 30), 'pulp'))
    assert len(after) == 1

    # Get lines after date, with one keywords list
    after = list(log.get_after(datetime(2017, 3, 27, 3, 20, 30), ['pulp', 'ERROR']))
    assert len(after) == 2
    after = list(log.get_after(datetime(2017, 3, 27, 3, 40, 30), 'pulp'))
    assert len(after) == 1
    # No lines are found
    assert list(log.get_after(datetime(2017, 3, 27, 3, 49, 46), 'pulp')) == []

    tmp_time = datetime(2017, 3, 27, 3, 39, 46)
    with pytest.raises(TypeError):
        list(log.get_after(tmp_time, ['type=', False, 'AVC']))
    with pytest.raises(TypeError):
        list(log.get_after(tmp_time, set(['type=', 'AVC'])))


def test_messages_get_after_bad_time_format():
    ctx = context_wrap(MESSAGES, path='/var/log/messages')
    log = FakeMessagesClass(ctx)
    assert len(log.lines) == 31

    # The timestamp format should only contain parts that get_after recognises
    with pytest.raises(ParseException) as exc:
        assert list(log.bad_get_after(datetime(2017, 3, 27, 3, 39, 46))) is None
    assert 'get_after does not understand strptime format ' in str(exc)


MESSAGES_ROLLOVER_YEAR = """
Dec 31 21:43:00 duradm13 [CMA]: Logger failed to open catalog file
Dec 31 22:03:05 duradm13 xinetd[21465]: START: bgssd pid=28021 from=10.20.40.7
Dec 31 22:03:05 duradm13 xinetd[21465]: EXIT: bgssd status=0 pid=28021 duration=0(sec)
Dec 31 23:03:07 duradm13 xinetd[21465]: START: bgssd pid=31307 from=10.20.40.7
Dec 31 23:03:07 duradm13 xinetd[21465]: EXIT: bgssd status=0 pid=31307 duration=0(sec)
Dec 31 23:07:00 duradm13 [CMA]: Logger failed to open catalog file
Jan  1 00:00:00 duradm13 [CMA]: Logger failed to open catalog file
Jan  1 00:03:09 duradm13 xinetd[21465]: START: bgssd pid=2203 from=10.20.40.7
Jan  1 00:03:09 duradm13 xinetd[21465]: EXIT: bgssd status=0 pid=2203 duration=0(sec)
Jan  1 00:11:45 duradm13 xinetd[21465]: START: vnetd pid=2670 from=10.20.40.36
Jan  1 00:11:47 duradm13 xinetd[21465]: START: vnetd pid=2671 from=10.20.40.36
Jan  1 00:11:48 duradm13 xinetd[21465]: EXIT: vnetd status=0 pid=2671 duration=1(sec)
Jan  1 01:00:08 duradm13 xinetd[21465]: START: nrpe pid=6189 from=10.20.40.240
Jan  1 01:00:08 duradm13 xinetd[21465]: EXIT: nrpe status=0 pid=6189 duration=0(sec)
Jan  1 01:00:27 duradm13 xinetd[21465]: START: nrpe pid=6207 from=10.20.40.240
Jan  1 01:00:27 duradm13 xinetd[21465]: EXIT: nrpe status=0 pid=6207 duration=0(sec)
Jan  1 01:00:29 duradm13 xinetd[21465]: START: nrpe pid=6210 from=10.20.40.240
Jan  1 01:00:29 duradm13 xinetd[21465]: EXIT: nrpe status=0 pid=6210 duration=0(sec)
""".strip()


def test_messages_log_time_wrap():
    # Check rollover process for when dates in logs without a year go from
    # December from January.
    ctx = context_wrap(MESSAGES_ROLLOVER_YEAR, path='/var/log/messages')
    log = FakeMessagesClass(ctx)
    assert len(log.lines) == 18

    # If sought date is in January, we should not get logs from December
    found = list(log.get_after(datetime(2017, 1, 1, 1, 0, 0)))
    assert len(found) == 6
    # If sought date is in December, we should get logs from January
    found = list(log.get_after(datetime(2017, 12, 31, 23, 0, 0)))
    assert len(found) == 15


HTTPD_ACCESS_LOG = """
192.168.220.42 - - [14/Feb/2016:03:18:54 -0600] "POST /XMLRPC HTTP/1.1" 200 1381 "-" "rhn.rpclib.py/$Revision$"
192.168.220.42 - - [14/Feb/2016:03:18:54 -0600] "POST /XMLRPC HTTP/1.1" 200 3282 "-" "rhn.rpclib.py/$Revision$"
192.168.220.42 - - [14/Feb/2016:03:18:54 -0600] "POST /XMLRPC HTTP/1.1" 200 163 "-" "rhn.rpclib.py/$Revision$"
192.168.220.42 - - [14/Feb/2016:03:18:54 -0600] "POST /XMLRPC HTTP/1.1" 200 138 "-" "rhn.rpclib.py/$Revision$"
192.168.128.243 - - [14/Feb/2016:03:19:00 -0600] "POST /cobbler_api HTTP/1.1" 200 144 "-" "Java/1.6.0"
192.168.128.243 - - [14/Feb/2016:03:19:00 -0600] "POST /cobbler_api HTTP/1.1" 200 129 "-" "Java/1.6.0"
192.168.128.243 - - [14/Feb/2016:03:20:00 -0600] "POST /cobbler_api HTTP/1.1" 200 144 "-" "Java/1.6.0"
192.168.128.243 - - [14/Feb/2016:03:20:00 -0600] "POST /cobbler_api HTTP/1.1" 200 129 "-" "Java/1.6.0"
"""


class FakeAccessLog(LogFileOutput):
    time_format = '%d/%b/%Y:%H:%M:%S'


def test_logs_with_year():
    ctx = context_wrap(HTTPD_ACCESS_LOG, path='/var/log/httpd/access_log')
    log = FakeAccessLog(ctx)
    assert len(log.lines) == 8

    assert len(list(log.get_after(datetime(2016, 2, 14, 3, 18, 55)))) == 4


DATE_CHANGE_MARIADB_LOG = """
161109  9:25:42 [Warning] SSL error: SSL_CTX_set_default_verify_paths failed
161109  9:25:42 [Note] WSREP: Service disconnected.
161109  9:25:43 [Note] WSREP: Some threads may fail to exit.
161109 14:28:24 InnoDB: Initializing buffer pool, size = 128.0M
161109 14:28:24 InnoDB: Completed initialization of buffer pool
2017-01-03 09:36:17 139651251140544 [Note] MariaDB 10.1.5 started successfully
"""


class FakeMariaDBLog(LogFileOutput):
    time_format = ['%y%m%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']


class DictMariaDBLog(LogFileOutput):
    time_format = {'old': '%y%m%d %H:%M:%S', 'new': '%Y-%m-%d %H:%M:%S'}


class BadClassMariaDBLog(LogFileOutput):
    time_format = FakeAccessLog


def test_logs_with_two_timestamps():
    ctx = context_wrap(DATE_CHANGE_MARIADB_LOG, path='/var/log/mariadb/mariadb.log')
    log = FakeMariaDBLog(ctx)
    assert len(log.lines) == 6

    new_ver = list(log.get_after(datetime(2017, 1, 1, 9, 0, 0)))
    assert len(new_ver) == 1
    assert new_ver[0]['raw_message'] == '2017-01-03 09:36:17 139651251140544 [Note] MariaDB 10.1.5 started successfully'

    dict_log = DictMariaDBLog(ctx)
    new_ver_d = list(dict_log.get_after(datetime(2017, 1, 1, 9, 0, 0)))
    assert len(new_ver_d) == 1
    assert new_ver_d[0]['raw_message'] == '2017-01-03 09:36:17 139651251140544 [Note] MariaDB 10.1.5 started successfully'

    # get_after should only supply a string or list for time_format
    with pytest.raises(ParseException) as exc:
        logerr = BadClassMariaDBLog(ctx)
        assert list(logerr.get_after(datetime(2017, 3, 27, 3, 39, 46))) is None
    assert 'get_after does not recognise time formats of type ' in str(exc)


MILLISECONDS_TOWER_LOG = """
2020-05-28 19:25:36,892 WARNING  django.request Not Found: /api/v1/me/
2020-05-28 19:25:46,944 INFO     awx.api.authentication User admin performed a GET to /api/v2/activity_stream/ through the API
2020-05-28 19:33:03,125 INFO     awx.api.authentication User admin performed a GET to /api/v2/job_templates/7/survey_spec/ through the API
2020-05-28 19:33:03,413 INFO     awx.api.authentication User admin performed a GET to /api/v2/projects/ through the API
""".strip()


class FakeTowerLog(LogFileOutput):
    time_format = '%Y-%m-%d %H:%M:%S,%f'


def test_logs_with_milliseconds():
    ctx = context_wrap(MILLISECONDS_TOWER_LOG, path='/var/log/tower/tower.log')
    log = FakeTowerLog(ctx)
    assert len(log.lines) == 4
    assert len(list(log.get_after(datetime(2020, 5, 28, 19, 25, 46, 944)))) == 3
