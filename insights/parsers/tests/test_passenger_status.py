from insights.parsers import SkipException
from insights.parsers import passenger_status
from insights.parsers.passenger_status import PassengerStatus
from insights.tests import context_wrap
import pytest
import doctest


PASS_STATUS = """
Version : 4.0.18
Date    : 2018-10-23 15:42:04 +0800
Instance: 1265
----------- General information -----------
Max pool size : 12
Processes     : 2
Requests in top-level queue : 0

----------- Application groups -----------
/usr/share/foreman#default:
  App root: /usr/share/foreman
  Requests in queue: 192
  * PID: 30131   Sessions: 1       Processed: 991     Uptime: 2h 9m 8s
    CPU: 3%      Memory  : 562M    Last used: 1h 53m 51s
  * PID: 32450   Sessions: 1       Processed: 966     Uptime: 2h 8m 15s
    CPU: 4%      Memory  : 463M    Last used: 1h 48m 17
  * PID: 4693    Sessions: 1       Processed: 939     Uptime: 2h 6m 32s
    CPU: 3%      Memory  : 470M    Last used: 1h 50m 48

/etc/puppet/rack#default:
  App root: /etc/puppet/rack
  Requests in queue: 0
  * PID: 21934   Sessions: 1       Processed: 380     Uptime: 1h 33m 34s
    CPU: 1%      Memory  : 528M    Last used: 1h 29m 4
  * PID: 26194   Sessions: 1       Processed: 544     Uptime: 1h 31m 34s
    CPU: 2%      Memory  : 490M    Last used: 1h 23m 5
  * PID: 32384   Sessions: 1       Processed: 36      Uptime: 1h 0m 29s
    CPU: 0%      Memory  : 561M    Last used: 1h 0m 3s
"""

PASS_STATUS_SP = """
Version : 4.0.18
Date    : 2019-06-10 03:17:38 +0100
Instance: 14745
----------- General information -----------
Max pool size : 60
Processes     : 7
Requests in top-level queue : 0

----------- Application groups -----------
/usr/share/foreman#default:
  App root: /usr/share/foreman
  Requests in queue: 0
  * PID: 39176  Sessions: 0     Processed: 194     Uptime: 24h 9m 0s
    CPU: 0%     Memory  : 488M  Last used: 20m 24s a
  * PID: 39342  Sessions: 0       Processed: 0       Uptime: 24h 8m 58s
    CPU: 0%     Memory  : 178M    Last used: 24h 8m 5
  * PID: 39377  Sessions: 0       Processed: 0       Uptime: 24h 8m 58s
    CPU: 0%     Memory  : 179M    Last used: 24h 8m 5
  * PID: 39478  Sessions: 0       Processed: 0       Uptime: 24h 8m 57s
    CPU: 0%     Memory  : 178M    Last used: 24h 8m 5
  * PID: 39525  Sessions: 0       Processed: 0       Uptime: 24h 8m 57s
    CPU: 0%     Memory  : 173M    Last used: 24h 8m 5
  * PID: 39614  Sessions: 0       Processed: 0       Uptime: 24h 8m 56s
    CPU: 0%     Memory  : 174M    Last used: 24h 8m 5

/etc/puppet/rack#default:
  App root: /etc/puppet/rack
  Requests in queue: 0
  * PID: 39667   Sessions: 0       Processed: 241     Uptime: 24h 8m 56s
    CPU: 0%      Memory  : 45M     Last used: 20m 24s
"""

PASS_STATUS_EXP1 = """
wrong content
"""


def test_passenger_status():
    passenger_status = PassengerStatus(context_wrap(PASS_STATUS))
    assert passenger_status["Version"] == '4.0.18'
    assert len(passenger_status['foreman_default']['p_list']) == 3
    assert 'rack_default' in passenger_status


def test_passenger_status_2():
    passenger_status = PassengerStatus(context_wrap(PASS_STATUS_SP))
    assert passenger_status["Version"] == '4.0.18'
    assert len(passenger_status['foreman_default']['p_list']) == 6
    foreman_default_p_list = passenger_status['foreman_default']['p_list']
    assert foreman_default_p_list[0] == {
            'PID': '39176', 'Sessions': '0', 'Processed': '194', 'Uptime': '24h 9m 0s',
            'CPU': '0%', 'Memory': '488M', 'Last used': '20m 24s a'}
    assert foreman_default_p_list[1] == {
            'PID': '39342', 'Sessions': '0', 'Processed': '0', 'Uptime': '24h 8m 58s',
            'CPU': '0%', 'Memory': '178M', 'Last used': '24h 8m 5'}
    assert foreman_default_p_list[-1] == {
            'PID': '39614', 'Sessions': '0', 'Processed': '0', 'Uptime': '24h 8m 56s',
            'CPU': '0%', 'Memory': '174M', 'Last used': '24h 8m 5'}
    assert 'rack_default' in passenger_status


def test_passenger_status_ex():
    with pytest.raises(SkipException):
        PassengerStatus(context_wrap(PASS_STATUS_EXP1))


def test_passenger_status_doc_examples():
    env = {
        'passenger_status': PassengerStatus(context_wrap(PASS_STATUS)),
    }
    failed, total = doctest.testmod(passenger_status, globs=env)
    assert failed == 0
