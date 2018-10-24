import doctest

from insights.parsers import ParseException
from insights.parsers import passenger_status
from insights.parsers.passenger_status import PassengerStatus
from insights.tests import context_wrap

import pytest


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

PASS_STATUS_EXP1 = """
wrong content
"""


def test_passenger_status():
    passenger_status = PassengerStatus(context_wrap(PASS_STATUS))
    assert passenger_status.data["Version"] == '4.0.18'
    assert len(passenger_status.data['foreman_default']['p_list']) == 3
    assert ('rack_default' in passenger_status.data) is True


def test_passenger_status_ex():
    with pytest.raises(ParseException) as pe:
        PassengerStatus(context_wrap(PASS_STATUS_EXP1))
        assert "Cannot find the header line." in str(pe)


def test_passenger_status_doc_examples():
    env = {
        'passenger_status': PassengerStatus(context_wrap(PASS_STATUS)),
    }
    failed, total = doctest.testmod(passenger_status, globs=env)
    assert failed == 0
