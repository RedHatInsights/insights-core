from falafel.tests import context_wrap
from falafel.mappers import rhn_server_xmlrpc

LOG_DATA = """
2016/04/11 05:52:01 -04:00 23630 10.4.4.17: xmlrpc/registration.welcome_message('lang: None',)
2016/04/11 05:52:26 -04:00 12911 10.4.4.17: xmlrpc/registration.create_system("token = '1-RegKey'", '6Server', 'x86_64')
2016/04/11 05:52:26 -04:00 12911 10.4.4.17: rhnServer/server_token.process_token(1000010125, 'enterprise_entitled,provisioning_entitled,virtualization_host')
2016/04/11 05:52:47 -04:00 23628 10.4.4.17: xmlrpc/registration.__add_hw_profile_no_auth(1000010125, 'items: 6')
2016/04/11 10:49:12 -04:00 11594 192.168.18.163: xmlrpc/registration.welcome_message('lang: None',)
2016/04/11 10:49:12 -04:00 11601 192.168.18.163: xmlrpc/registration.register_osad
2016/04/11 10:49:17 -04:00 11599 192.168.18.163: xmlrpc/registration.register_osad_jid
2016/04/11 12:57:26 -04:00 11594 192.168.18.28: rhnServer/server_certificate.valid('Server id ID-1000010124 not found in database',)
"""


def test_log_data():
    log = rhn_server_xmlrpc.ServerXMLRPCLog(context_wrap(LOG_DATA))

    print log

    # Check the first log line for all fields
    line = log.get('10.4.4.17: xmlrpc/registration.welcome_message')[0]
    
    line['timestamp'] = '2016/04/11 05:52:01 -04:00'
    line['pid'] = '23630'
    line['client_ip'] = '10.4.4.17'
    line['module'] = 'xmlrpc'
    line['function'] = 'registration.welcome_message'
    line['client_id'] = None
    line['args'] = "'lang: None',"

