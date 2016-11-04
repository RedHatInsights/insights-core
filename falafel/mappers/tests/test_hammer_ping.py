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

HAMMERPING_RETURNVALUE = """
{
        'candlepin':
            {'FAIL': '404 Resource Not Found'},
        'candlepin_auth':
            {'FAIL': 'Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found <html>... (skipping some generic 404 html page details) </html> (GET /candlepin/status)'},
        'foreman_tasks':
            {'ok': '1ms'},
        'elasticsearch':
            {'ok': '35ms'},
        'pulp_auth':
            {'ok': '27ms'},
        'pulp':
            {'ok': '61ms'}
}
"""


def test_hammer_ping():
    dic = hammer_ping.HammerPing(context_wrap(HAMMERPING)).data

    assert dic.keys() == ['candlepin', 'candlepin_auth', 'foreman_tasks', 'elasticsearch', 'pulp_auth', 'pulp']
    assert dic.values() == [{'FAIL': '404 Resource Not Found'}, {'FAIL': 'Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found <html>... (skipping some generic 404 html page details) </html> (GET /candlepin/status)'}, {'ok': '1ms'}, {'ok': '35ms'}, {'ok': '27ms'}, {'ok': '61ms'}]
    assert dic.get('candlepin') == {'FAIL': '404 Resource Not Found'}
    assert dic.get('candlepin').get('FAIL') == '404 Resource Not Found'

    # Because of the key which equal to 'ok' isn't the dic['candlepin']'s key,in this case, after print dic['candlepin']['ok'],  it will output:KeyError:'ok'So,while using this mapper.Only thing you need to do is sure the return_value of dic['xxx'].get('FAIL',-1) ,if return_value equal to -1,indicate that status isright,maybe you can ignore the right message,else FAIL,at the same time you can use the fail message
    assert dic['candlepin'].get('FAIL', -1) != -1
    assert dic['candlepin'].get('FAIL', -1) == '404 Resource Not Found'

    assert dic.get('candlepin_auth') == {'FAIL': 'Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found <html>... (skipping some generic 404 html page details) </html> (GET /candlepin/status)'}
    assert dic.get('candlepin_auth').get('FAIL') == 'Katello::Resources::Candlepin::CandlepinPing: 404 Resource Not Found <html>... (skipping some generic 404 html page details) </html> (GET /candlepin/status)'
    assert dic['candlepin_auth'].get('FAIL', -1) != -1

    assert dic.get('pulp_auth') == {'ok': '27ms'}
    assert dic['pulp_auth'].get('ok') == '27ms'
    assert dic['pulp_auth'].get('FAIL', -1) == -1

    assert len(dic) == 6
    assert eval(HAMMERPING_RETURNVALUE) == dic
