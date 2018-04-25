import doctest

from insights.parsers import vdsm_logger_conf
from insights.tests import context_wrap

CONF = '''
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


def test_vdsm_logger_conf():
    conf = vdsm_logger_conf.VDSMLoggerConf(context_wrap(CONF))
    assert len(conf.sections()) == 18
    assert conf.has_option('loggers', 'keys') is True
    assert conf.getboolean('logger_root', 'propagate') is False
    assert conf.get('logger_ovirt_hosted_engine_ha', 'level') == 'DEBUG'
    assert conf.get('formatter_sysform', 'datefmt') == ''
    assert conf.has_option('formatter_long', 'class') is True
    assert conf.items('loggers') == {'keys': 'root,vds,storage,virt,ovirt_hosted_engine_ha,ovirt_hosted_engine_ha_config,IOProcess,devel'}


def test_vdsm_logger_conf_documentation():
    failed_count, tests = doctest.testmod(
        vdsm_logger_conf,
        globs={'conf': vdsm_logger_conf.VDSMLoggerConf(context_wrap(CONF))}
    )
    assert failed_count == 0
