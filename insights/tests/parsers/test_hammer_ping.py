import doctest
import pytest

from insights.core.exceptions import SkipComponent
from insights.parsers import hammer_ping
from insights.parsers.hammer_ping import HammerPing
from insights.tests import context_wrap

HAMMERPING_ERR_1 = """
Error: Connection refused - connect(2) for "localhost" port 443
"""

HAMMERPING_ERR_2 = """
Could not load the API description from the server
 - is the server down?
 - was 'foreman-rake apipie:cache' run on the server when using apipie cache? (typical production settings)
Warning: An error occured while loading module hammer_cli_csv
Could not load the API description from the server
 - is the server down?
 - was 'foreman-rake apipie:cache' run on the server when using apipie cache? (typical production settings)
Warning: An error occured while loading module hammer_cli_foreman
"""

HAMMERPING_OK_1 = """
candlepin:
    Status:          ok
    Server Response: Duration: 61ms
candlepin_auth:
    Status:          ok
"""

HAMMERPING_ERR_3 = """
database:
   Status:          ok
   Server Response: Duration: 0ms
katello_agent:
   Status:          ok
   message:         0 Processed, 0 Failed
   Server Response: Duration: 0ms
candlepin:
   Status:          ok
   Server Response: Duration: 45ms
candlepin_auth:
   Status:          ok
   Server Response: Duration: 45ms
candlepin_events:
   Status:          ok
   message:         0 Processed, 0 Failed
   Server Response: Duration: 0ms
katello_events:
   Status:          ok
   message:         0 Processed, 0 Failed
   Server Response: Duration: 0ms
pulp3:
   Status:          ok
   Server Response: Duration: 294ms
pulp3_content:
   Status:          ok
   Server Response: Duration: 58ms
foreman_tasks:
   Status:          ok
   Server Response: Duration: 3ms

2 more service(s) failed, but not shown:
pulp, pulp_auth
"""

HAMMERPING_OK = """
candlepin:
    Status:          ok
    Server Response: Duration: 61ms
candlepin_auth:
    Status:          ok
    Server Response: Duration: 61ms
pulp:
    Status:          ok
    Server Response: Duration: 61ms
pulp_auth:
    Status:          ok
    Server Response: Duration: 61ms
elasticsearch:
    Status:          ok
    Server Response: Duration: 35ms
foreman_tasks:
    Status:          ok
    server Response: Duration: 1ms
""".strip()

HAMMERPING_COMMAND = """
COMMAND> hammer ping

candlepin:
    Status:          ok
    Server Response: Duration: 20ms
candlepin_auth:
    Status:          ok
    Server Response: Duration: 14ms
pulp:
    Status:          ok
    Server Response: Duration: 101ms
pulp_auth:
    Status:          ok
    Server Response: Duration: 75ms
foreman_tasks:
    Status:          ok
    Server Response: Duration: 3ms

""".strip()

HAMMERPING = """
candlepin:
    Status:          FAIL
    Server Response:Message:404 Resource Not Found
candlepin_auth:
    Status:          FAIL
    Server Response: Message: Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found
pulp:
    Status:          ok
    Server Response: Duration: 61ms
pulp_auth:
    Status:
    Server Response:
elasticsearch:
    Status:          ok
    Server Response: Duration: 35ms
foreman_tasks:
    Status:          ok
    server Response: Duration: 1ms
""".strip()

HAMMERPING_FAIL = """
candlepin:
    Status:          ok
    Server Response:
candlepin_auth:
    Status:          ok
    Server Response:
pulp:
    Status:          FAIL
    Server Response:
pulp_auth:
    Status: FAIL
foreman_tasks:
    Status:          ok
    Server Response: Duration: 28ms
""".strip()

HAMMERPING_EXAMPLE = """
candlepin:
    Status:          FAIL
    Server Response: Message: 404 Resource Not Found
elasticsearch:
    Status:          ok
    Server Response: Duration: 35ms
foreman_tasks:
    Status:          ok
    Server Response: Duration: 1ms
""".strip()

HAMMERPING_EMPTY = """
COMMAND> hammer ping

""".strip()


def test_hammer_ping_err_1():
    status = HammerPing(context_wrap(HAMMERPING_ERR_1))
    assert not status.are_all_ok
    assert status.errors != []


def test_hammer_ping_err_2():
    status = HammerPing(context_wrap(HAMMERPING_ERR_2))
    assert not status.are_all_ok
    assert status.errors != []


def test_hammer_ping_err_3():
    status = HammerPing(context_wrap(HAMMERPING_OK_1))
    assert status.are_all_ok
    assert status.errors == []


def test_hammer_ping_err_4():
    status = HammerPing(context_wrap(HAMMERPING_ERR_3))
    assert not status.are_all_ok
    assert status.errors != []


def test_hammer_ping_ok():
    status = HammerPing(context_wrap(HAMMERPING_OK))

    assert status.are_all_ok
    assert status.service_list == [
        'candlepin', 'candlepin_auth', 'elasticsearch', 'foreman_tasks', 'pulp', 'pulp_auth',
    ]
    assert status.services_of_status('FAIL') == []
    assert 'nonexistent' not in status.service_list


def test_hammer_ping_command():
    status = HammerPing(context_wrap(HAMMERPING_COMMAND))

    assert status.are_all_ok
    assert status.service_list == [
        'candlepin', 'candlepin_auth', 'foreman_tasks', 'pulp', 'pulp_auth',
    ]
    assert status.services_of_status('FAIL') == []
    assert 'nonexistent' not in status.service_list


def test_hammer_ping():
    status = HammerPing(context_wrap(HAMMERPING))

    assert not status.are_all_ok
    assert status.service_list == [
        'candlepin', 'candlepin_auth', 'elasticsearch', 'foreman_tasks',
        'pulp', 'pulp_auth'
    ]
    assert status.services_of_status('OK') == [
        'elasticsearch', 'foreman_tasks', 'pulp'
    ]
    assert status.services_of_status('FAIL') == [
        'candlepin', 'candlepin_auth'
    ]
    assert status['pulp_auth']['Status'] == ''
    assert status['candlepin']['Status'] == 'FAIL'
    assert status['elasticsearch']['Status'] == 'ok'
    assert status['pulp_auth']['Server Response'] == ''
    assert status['candlepin_auth']['Server Response'] == 'Message: Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found'
    assert status['elasticsearch']['Server Response'] == 'Duration: 35ms'

    assert 'nonexistent' not in status.service_list
    assert 'nonexistent' not in status


def test_hammer_different_lines():
    status = HammerPing(context_wrap(HAMMERPING_FAIL))
    assert status.services_of_status('FAIL') == [
        'pulp', 'pulp_auth'
    ]

    assert status.services_of_status('ok') == [
        'candlepin', 'candlepin_auth', 'foreman_tasks'
    ]


def test_status_and_response():
    status = HammerPing(context_wrap(HAMMERPING_FAIL))
    assert status.status_of_service['pulp'] == 'fail'
    assert status.status_of_service['foreman_tasks'] == 'ok'

    assert status.response_of_service['pulp'] == ''
    assert status.response_of_service['foreman_tasks'] == 'Duration: 28ms'


def test_raw_content():
    status = HammerPing(context_wrap(HAMMERPING_COMMAND))
    for line in HAMMERPING_COMMAND.splitlines():
        assert line in status.raw_content


def test_content_empty():
    with pytest.raises(SkipComponent):
        HammerPing(context_wrap(HAMMERPING_EMPTY))


def test_losetup_doc_examples():
    env = {'hammer_ping': HammerPing(context_wrap(HAMMERPING_EXAMPLE))}
    failed, total = doctest.testmod(hammer_ping, globs=env)
    assert failed == 0
