from falafel.mappers import hammer_ping
from falafel.tests import context_wrap

HAMMERPING = """
candlepin:
    Status:          FAIL
    Server Response:Message:404 Resource Not Found
candlepin_auth:
    Status:          FAIL
    Server Response: Message: Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found <html>... (skipping some generic 404 html page details) </html> (GET /candlepin/status)
pulp:
    Status:          ok
    Server Response: Duration: 61ms
pulp_auth:
    Status:          ok
    Server Response: Duration: 27ms
elasticsearch:
    Status:          ok
    Server Response: Duration: 35ms
foreman_tasks:
    Status:          ok
    server Response: Duration: 1ms
""".strip()


def test_hammer_ping():
    status = hammer_ping.HammerPing(context_wrap(HAMMERPING))
    dic = status.data

    assert len(status) == 6
    assert len(dic) == 6

    assert dic.keys() == [
        'candlepin', 'candlepin_auth', 'foreman_tasks', 'elasticsearch',
        'pulp_auth', 'pulp'
    ]

    assert dic['candlepin'].keys() == ['status', 'response']
    assert dic['candlepin']['status'] == 'FAIL'
    assert dic['candlepin']['response'] == '404 Resource Not Found'

    assert dic['pulp_auth']['status'] == 'ok'
    assert dic['pulp_auth']['response'] == '27ms'

    assert not status.is_ok('candlepin_auth')
    assert status.is_ok('pulp')

    assert status.response_of('candlepin') == '404 Resource Not Found'
    assert status.response_of('elasticsearch') == '35ms'

    # A service that isn't in the list should return false values
    assert not status.is_ok('nonexistent')
    assert status.response_of('nonexistent') == ''
