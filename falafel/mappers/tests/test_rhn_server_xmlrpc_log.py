from falafel.tests import context_wrap
from falafel.mappers import rhn_server_xmlrpc

import datetime

LOG_DATA = """
2016/04/11 05:52:01 -04:00 23630 10.4.4.17: xmlrpc/registration.welcome_message('lang: None',)
2016/04/11 05:52:26 -04:00 12911 10.4.4.17: xmlrpc/registration.create_system("token = '1-RegKey'", '6Server', 'x86_64')
2016/04/11 05:52:26 -04:00 12911 10.4.4.17: rhnServer/server_token.process_token(1000010125, 'enterprise_entitled,provisioning_entitled,virtualization_host')
2016/04/11 05:52:47 -04:00 23628 10.4.4.17: xmlrpc/registration.__add_hw_profile_no_auth(1000010125, 'items: 6')
2016/04/11 10:49:12 -04:00 11594 192.168.18.163: xmlrpc/registration.welcome_message('lang: None',)
2016/04/11 10:49:12 -04:00 11601 192.168.18.163: xmlrpc/registration.register_osad
2016/04/11 10:49:17 -04:00 11599 192.168.18.163: xmlrpc/registration.register_osad_jid
2016/04/11 12:57:26 -04:00 11594 192.168.18.28: rhnServer/server_certificate.valid('Server id ID-1000010124 not found in database',)
2016/07/27 04:44:41 -04:00 25923 2620:10a:0:4::40: xmlrpc/queue.get(1000014812, 2, 'checkins enabled')
"""

def test_log_data():
    log = rhn_server_xmlrpc.ServerXMLRPCLog(context_wrap(LOG_DATA))

    # Check the first log line for all fields
    line = log.get('10.4.4.17: xmlrpc/registration.welcome_message')[0]

    assert line['timestamp'] == '2016/04/11 05:52:01 -04:00'
    d = datetime.datetime(2016, 04, 11, 05, 52, 01)
    assert line['datetime'] == d
    assert line['pid'] == '23630'
    assert line['client_ip'] == '10.4.4.17'
    assert line['module'] == 'xmlrpc'
    assert line['function'] == 'registration.welcome_message'
    assert line['client_id'] is None
    assert line['args'] == "'lang: None'"

    # Check that get works
    assert len(log.get('welcome_message')) == 2

    # Check that __contains__ works
    assert 'welcome_message' in log

    # Check parsing of lines without argument lists
    line = log.get('registration.register_osad_jid')[0]
    assert line['args'] is None

    # Check lines that include the client ID
    line = log.get('__add_hw_profile_no_auth')[0]
    assert line['client_id'] == '1000010125'
    assert line['args'] == "'items: 6'"

    # Check that we can get IPv6 addresses correctly
    line = log.get('checkins enabled')[0]
    assert line['client_ip'] == '2620:10a:0:4::40'
    assert line['client_id'] == '1000014812'
    assert line['args'] == "2, 'checkins enabled'"
