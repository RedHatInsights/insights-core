import doctest

from insights.parsers import designate_conf
from insights.tests import context_wrap

DESIGNATE_CONF = """
[DEFAULT]
state_path=/var/lib/designate
debug=True
log_dir=/var/log/designate

[keystone_authtoken]
www_authenticate_uri=http://localhost:5000
project_name=service
project_domain_name=Default

[oslo_messaging_notifications]
driver=messagingv2
"""


def test_doc_examples():
    failed_count, tests = doctest.testmod(
        designate_conf,
        globs={'conf': designate_conf.DesignateConf(context_wrap(DESIGNATE_CONF))}
    )
    assert failed_count == 0


def test_designate_conf():
    dconf = designate_conf.DesignateConf(context_wrap(DESIGNATE_CONF))
    assert dconf is not None
    assert list(dconf.sections()) == ['keystone_authtoken', 'oslo_messaging_notifications']
    assert dconf.defaults() == {
        'debug': 'True',
        'state_path': '/var/lib/designate',
        'log_dir': '/var/log/designate'}
    assert dconf.get('keystone_authtoken', 'project_name') == 'service'
    assert dconf.has_option('oslo_messaging_notifications', 'driver')
    assert not dconf.has_option('yabba', 'dabba_do')
    assert dconf.get('DEFAULT', 'debug') == 'True'
