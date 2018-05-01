import doctest

from insights.parsers import vmware_tools_conf
from insights.tests import context_wrap

CONF = '''
[guestinfo]
disable-query-diskinfo = true

[logging]
log = true

vmtoolsd.level = debug
vmtoolsd.handler = file
vmtoolsd.data = /tmp/vmtoolsd.log
'''


def test_vmware_tools_conf():
    conf = vmware_tools_conf.VMwareToolsConf(context_wrap(CONF))
    assert list(conf.sections()) == ['guestinfo', 'logging']
    assert conf.has_option('guestinfo', 'disable-query-diskinfo') is True
    assert conf.getboolean('guestinfo', 'disable-query-diskinfo') is True
    assert conf.get('guestinfo', 'disable-query-diskinfo') == 'true'
    assert conf.get('logging', 'vmtoolsd.handler') == 'file'
    assert conf.get('logging', 'vmtoolsd.data') == '/tmp/vmtoolsd.log'


def test_vmware_tools_conf_documentation():
    failed_count, tests = doctest.testmod(
        vmware_tools_conf,
        globs={'conf': vmware_tools_conf.VMwareToolsConf(context_wrap(CONF))}
    )
    assert failed_count == 0
