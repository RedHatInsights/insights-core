"""
VDSM logger configuration file - ``/etc/vdsm/logger.conf``
==========================================================

The VDSM logger configuration file ``/etc/vdsm/logger.conf``
is in the standard 'ini' format and is read by the IniConfigFile
parser.


Sample ``/etc/vdsm/logger.conf`` file::

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

Examples:

    >>> len(conf.sections())
    18
    >>> conf.has_option('formatter_long', 'class')
    True
    >>> conf.has_option('loggers', 'keys')
    True
    >>> conf.getboolean('logger_root', 'propagate')
    False
    >>> conf.items('loggers')
    {'keys': 'root,vds,storage,virt,ovirt_hosted_engine_ha,ovirt_hosted_engine_ha_config,IOProcess,devel'}
    >>> conf.get('logger_ovirt_hosted_engine_ha', 'level')
    'DEBUG'
    >>> conf.get('formatter_sysform', 'datefmt')
    ''
"""
from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.vdsm_logger_conf)
class VDSMLoggerConf(IniConfigFile):
    """Parse VDSM logger configuration file content."""
    pass
