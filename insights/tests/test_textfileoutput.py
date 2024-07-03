# -*- coding: UTF-8 -*-
import pytest

from insights.core import TextFileOutput
from insights.tests import context_wrap


class FakeMessagesClass(TextFileOutput):
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


def test_lines_scanners():
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

    def count_lost_lines(self):
        imuxsock_lines = 0
        lost_lines = 0
        for line in self.lines:
            if 'imuxsock lost' in line:
                parts = line.split(None)
                if parts[7].isdigit():
                    imuxsock_lines += 1
                    lost_lines += int(parts[7])
        return "lost {msgs} lines in {lines} lines".format(msgs=lost_lines, lines=imuxsock_lines)
    FakeMessagesClass.scan('lost_lines', count_lost_lines)

    ctx = context_wrap(MESSAGES, path='/var/log/messages')
    log = FakeMessagesClass(ctx)
    assert hasattr(log, 'puppet_master_logs')
    assert hasattr(log, 'kernel_logs')
    assert hasattr(log, 'middleware_exception_present')
    assert hasattr(log, 'cron_present')
    assert hasattr(log, 'lost_lines')

    assert len(log.puppet_master_logs) == 6
    assert log.puppet_master_logs[0]['raw_line'] == 'Mar 27 03:18:24 system puppet-master[48226]: Setting manifest is deprecated in puppet.conf. See http://links.puppetlabs.com/env-settings-deprecations'
    assert log.kernel_logs == []
    assert log.middleware_exception_present
    assert not log.cron_present
    assert log.lost_lines == 'lost 451 lines in 3 lines'


def test_lines_scanners_list():
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
    assert 'puppet-master' in log.puppet_master_manifest_last['raw_line']
    assert 'manifest' in log.puppet_master_manifest_last['raw_line']
    assert hasattr(log, 'puppet_master_first_last_any')
    assert 'puppet-master' in log.puppet_master_first_last_any['raw_line']


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


def test_lines_2():
    ctx = context_wrap(MESSAGES_ROLLOVER_YEAR, path='/var/log/messages')
    log = FakeMessagesClass(ctx)
    assert len(log.lines) == 18
