import doctest

from insights.parsers import vdsm_conf
from insights.tests import context_wrap


VDSM_CONF = '''
[vars]
ssl = true
cpu_affinity = 1

[addresses]
management_port = 54321
qq = 345
'''

VDSM_LOGGER_CONF = '''
[loggers]
keys=root,vds,storage,virt,ovirt_hosted_engine_ha,ovirt_hosted_engine_ha_config,IOProcess,devel

[handlers]
keys=console,syslog,logfile

[formatters]
keys=long,simple,none,sysform

[logger_root]
level=DEBUG
handlers=syslog,logfile
propagate=0

[logger_vds]
level=DEBUG
handlers=syslog,logfile
qualname=vds
propagate=0

[logger_storage]
level=DEBUG
handlers=logfile
qualname=storage
propagate=0

[logger_ovirt_hosted_engine_ha]
level=DEBUG
handlers=
qualname=ovirt_hosted_engine_ha
propagate=1

[logger_ovirt_hosted_engine_ha_config]
level=DEBUG
handlers=
qualname=ovirt_hosted_engine_ha.env.config
propagate=0

[logger_IOProcess]
level=DEBUG
handlers=logfile
qualname=IOProcess
propagate=0

[logger_virt]
level=DEBUG
handlers=logfile
qualname=virt
propagate=0

[logger_devel]
level=DEBUG
handlers=logfile
qualname=devel
propagate=0

[handler_syslog]
level=WARN
class=handlers.SysLogHandler
formatter=sysform
args=('/dev/log', handlers.SysLogHandler.LOG_USER)

[handler_logfile]
class=vdsm.logUtils.UserGroupEnforcingHandler
args=('vdsm', 'kvm', '/var/log/vdsm/vdsm.log',)
filters=storage.misc.TracebackRepeatFilter
level=DEBUG
formatter=long

[handler_console]
class: StreamHandler
args: []
formatter: none

[formatter_simple]
format: %(asctime)s:%(levelname)s:%(message)s

[formatter_none]
format: %(message)s

[formatter_long]
format: %(asctime)s %(levelname)-5s (%(threadName)s) [%(name)s] %(message)s (%(module)s:%(lineno)d)
class: vdsm.logUtils.TimezoneFormatter

[formatter_sysform]
format= vdsm %(name)s %(levelname)s %(message)s
datefmt=
'''


def test_vdsm_conf_ini():
    result = vdsm_conf.VDSMConfIni(context_wrap(VDSM_CONF))
    assert sorted(result.sections()) == sorted(['vars', 'addresses'])
    assert result.has_option('vars', 'ssl')
    assert result.getboolean('vars', 'ssl')
    assert result.getint('vars', 'cpu_affinity') == 1
    assert result.getint('addresses', 'management_port') == 54321
    assert result.getint('addresses', 'qq') == 345


def test_vdsm_logger_conf():
    conf = vdsm_conf.VDSMLoggerConf(context_wrap(VDSM_LOGGER_CONF))
    assert len(conf.sections()) == 18
    assert conf.has_option('loggers', 'keys') is True
    assert conf.getboolean('logger_root', 'propagate') is False
    assert conf.get('logger_ovirt_hosted_engine_ha', 'level') == 'DEBUG'
    assert conf.get('formatter_sysform', 'datefmt') == ''
    assert conf.has_option('formatter_long', 'class') is True
    assert conf.items('loggers') == {'keys': 'root,vds,storage,virt,ovirt_hosted_engine_ha,ovirt_hosted_engine_ha_config,IOProcess,devel'}


def test_documentation():
    env = {'conf': vdsm_conf.VDSMConfIni(context_wrap(VDSM_CONF)),
           'vdsm_logger_conf': vdsm_conf.VDSMLoggerConf(context_wrap(VDSM_LOGGER_CONF))}
    failed_count, tests = doctest.testmod(vdsm_conf, globs=env)
    assert failed_count == 0
