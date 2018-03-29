from insights.parsers.heat_conf import HeatConf
from insights.tests import context_wrap

HEAT_CONFIG = """
[DEFAULT]
heat_metadata_server_url = http://172.16.0.11:8000
heat_waitcondition_server_url = http://172.16.0.11:8000/v1/waitcondition
heat_watch_server_url =http://172.16.0.11:8003
stack_user_domain_name = heat_stack
stack_domain_admin = heat_stack_domain_admin
stack_domain_admin_password = *********
auth_encryption_key = mysupersecretkey
log_dir = /var/log/heat
instance_user=
notification_driver=messaging
[auth_password]
[clients]
[clients_ceilometer]
[clients_cinder]
[clients_glance]
[clients_heat]
[clients_keystone]
auth_uri =http://192.0.2.18:35357
[clients_neutron]
[clients_nova]
[clients_sahara]
[clients_swift]
[clients_trove]
[cors]
[cors.subdomain]
[database]
connection = *********
[ec2authtoken]
auth_uri = http://172.16.0.11:5000/v2.0/ec2tokens
[eventlet_opts]
[heat_api]
bind_host = 172.16.0.15
workers = 0
[heat_api_cfn]
bind_host = 172.16.0.15
workers = 0
[heat_api_cloudwatch]
bind_host = 172.16.0.15
workers = 0
""".strip()


def test_heat_conf():
    h_conf = HeatConf(context_wrap(HEAT_CONFIG))
    assert h_conf.get('DEFAULT', 'heat_metadata_server_url') == 'http://172.16.0.11:8000'
    assert h_conf.get('DEFAULT', 'stack_user_domain_name') == 'heat_stack'
    assert h_conf.get('clients_keystone', 'auth_uri') == 'http://192.0.2.18:35357'
    assert h_conf.get('heat_api_cloudwatch', 'bind_host') == '172.16.0.15'
