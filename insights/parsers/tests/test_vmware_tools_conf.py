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
    result = vmware_tools_conf.VMwareToolsConf(context_wrap(CONF))
    assert result.sections() == ['guestinfo', 'logging']
    assert result.has_option('guestinfo', 'disable-query-diskinfo') is True
    assert result.getboolean('guestinfo', 'disable-query-diskinfo') is True
    assert result.get('guestinfo', 'disable-query-diskinfo') == 'true'
    assert result.get('logging', 'vmtoolsd.handler') == 'file'
    assert result.get('logging', 'vmtoolsd.data') == '/tmp/vmtoolsd.log'


def test_vmware_tools_conf_documentation():
    failed_count, tests = doctest.testmod(vmware_tools_conf)
    assert failed_count == 0
