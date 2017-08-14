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

HAMMERPING_ERR_3 = """
candlepin:
    Status:          ok
    Server Response: Duration: 61ms
candlepin_auth:
    Status:          ok
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


def test_hammer_ping_err_1():
    status = HammerPing(context_wrap(HAMMERPING_ERR_1))
    assert not status.are_all_ok
    assert status.errors is not []


def test_hammer_ping_err_2():
    status = HammerPing(context_wrap(HAMMERPING_ERR_2))
    assert not status.are_all_ok
    assert status.errors is not []


def test_hammer_ping_err_3():
    status = HammerPing(context_wrap(HAMMERPING_ERR_3))
    assert not status.are_all_ok
    assert status.errors is not []


def test_hammer_ping_ok():
    status = HammerPing(context_wrap(HAMMERPING_OK))

    assert status.are_all_ok
    assert status.service_list == [
        'candlepin', 'candlepin_auth', 'pulp', 'pulp_auth',
        'elasticsearch', 'foreman_tasks'
    ]
    assert status.services_of_status('FAIL') == []
    assert 'nonexistent' not in status.service_list
    assert 'nonexistent' not in status.status_of_service
    assert 'nonexistent' not in status.response_of_service


def test_hammer_ping():
    status = HammerPing(context_wrap(HAMMERPING))

    assert not status.are_all_ok
    assert status.service_list == [
        'candlepin', 'candlepin_auth', 'pulp', 'pulp_auth',
        'elasticsearch', 'foreman_tasks'
    ]
    assert status.services_of_status('OK') == [
        'pulp', 'elasticsearch', 'foreman_tasks'
    ]
    assert status.services_of_status('FAIL') == [
        'candlepin', 'candlepin_auth'
    ]
    assert status.status_of_service['pulp_auth'] == ''
    assert status.status_of_service['candlepin'] == 'fail'
    assert status.status_of_service['elasticsearch'] == 'ok'
    assert status.response_of_service['pulp_auth'] == ''
    assert status.response_of_service['candlepin_auth'] == 'Message: Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found'
    assert status.response_of_service['elasticsearch'] == 'Duration: 35ms'

    assert 'nonexistent' not in status.service_list
    assert 'nonexistent' not in status.status_of_service
    assert 'nonexistent' not in status.response_of_service
