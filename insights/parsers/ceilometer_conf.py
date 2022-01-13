"""
CeilometerConf - file ``/etc/ceilometer/ceilometer.conf``
=========================================================
"""
from insights.core import IniConfigFile
from insights.core.plugins import parser
from insights.specs import Specs


@parser(Specs.ceilometer_conf)
class CeilometerConf(IniConfigFile):
    """
    The ``/etc/ceilometer/ceilometer.conf`` file is in a standard '.ini' format,
    and this parser uses the IniConfigFile base class to read this.

    Given a file containing the following test data::

        [DEFAULT]
        #
        # From ceilometer
        http_timeout = 600
        debug = False
        verbose = False
        log_dir = /var/log/ceilometer
        meter_dispatcher=database
        event_dispatcher=database
        [alarm]
        evaluation_interval = 60
        evaluation_service=ceilometer.alarm.service.SingletonAlarmService
        partition_rpc_topic=alarm_partition_coordination
        [api]
        port = 8777
        host = 192.0.2.10
        [central]
        [collector]
        udp_address = 0.0.0.0
        udp_port = 4952
        [compute]
        [coordination]
        backend_url = redis://:chDWmHdH8dyjsmpCWfCEpJR87@192.0.2.7:6379/

    Examples:
        >>> type(config)
        <class 'insights.parsers.ceilometer_conf.CeilometerConf'>
        >>> config.sections()
        ['alarm', 'api', 'central', 'collector', 'compute', 'coordination']
        >>> config.has_option('alarm', 'evaluation_interval')
        True
        >>> config.get('coordination', 'backend_url')
        'redis://:chDWmHdH8dyjsmpCWfCEpJR87@192.0.2.7:6379/'
        >>> config.getint('collector', 'udp_port')
        4952
        >>> config.getboolean('DEFAULT', 'debug')
        False
    """
    pass
