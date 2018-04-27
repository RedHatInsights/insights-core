"""
VDSMConfIni & VDSMLoggerConf
============================
"""

from .. import IniConfigFile, parser
from insights.specs import Specs


@parser(Specs.vdsm_conf)
class VDSMConfIni(IniConfigFile):
    """``VDSMConfIni`` parsers configuration file ``/etc/vdsm/vdsm.conf``
    format and is read by the IniConfigFile parser.

    Sample configuration file::

        [vars]
        ssl = true
        cpu_affinity = 1

        [addresses]
        management_port = 54321
        qq = 345


    Examples:
        >>> 'vars' in conf
        True
        >>> conf.get('addresses', 'qq')
        '345'
        >>> conf.getboolean('vars', 'ssl')
        True
        >>> conf.getint('addresses', 'management_port')
        54321

    """
    pass


@parser(Specs.vdsm_logger_conf)
class VDSMLoggerConf(IniConfigFile):
    """``VDSMLoggerConf`` parsers configuration file
    ``/etc/vdsm/logger.conf`` format and is read by the IniConfigFile
    parser.

    Sample configuration file::

        [loggers]
        keys=root,vds,storage,virt,ovirt_hosted_engine_ha,ovirt_hosted_engine_ha_config,IOProcess,devel

        [formatter_long]
        format: %(asctime)s %(levelname)-5s (%(threadName)s) [%(name)s] %(message)s (%(module)s:%(lineno)d)
        class: vdsm.logUtils.TimezoneFormatter

        [logger_root]
        level=DEBUG
        handlers=syslog,logfile
        propagate=0

        [formatters]
        keys=long,simple,none,sysform

        [logger_ovirt_hosted_engine_ha]
        level=DEBUG
        handlers=
        qualname=ovirt_hosted_engine_ha
        propagate=1

        [formatter_sysform]
        format= vdsm %(name)s %(levelname)s %(message)s
        datefmt=

    Examples:
        >>> len(vdsm_logger_conf.sections())
        18
        >>> vdsm_logger_conf.has_option('formatter_long', 'class')
        True
        >>> vdsm_logger_conf.has_option('loggers', 'keys')
        True
        >>> vdsm_logger_conf.getboolean('logger_root', 'propagate')
        False
        >>> vdsm_logger_conf.items('loggers')
        {'keys': 'root,vds,storage,virt,ovirt_hosted_engine_ha,ovirt_hosted_engine_ha_config,IOProcess,devel'}
        >>> vdsm_logger_conf.get('logger_ovirt_hosted_engine_ha', 'level')
        'DEBUG'
        >>> vdsm_logger_conf.get('formatter_sysform', 'datefmt')
        ''

    """
    pass
