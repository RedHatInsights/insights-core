"""
CeilometerConf - file ``/etc/ceilometer/ceilometer.conf``
=========================================================

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

Example:
    >>> config = shared[CeilometerConf]
    >>> config.sections()
    ['DEFAULT', 'alarm', 'api', 'central', 'collector', 'compute', 'coordination']
    >>> config.items('api')
    ['port', 'host']
    >>> config.has_option('alarm', 'evaluation_interval')
    True
    >>> config.get('coordination', 'backend_url')
    'redis://:chDWmHdH8dyjsmpCWfCEpJR87@192.0.2.7:6379/'
    >>> config.getint('collector', 'udp_port')
    4952
    >>> config.getboolean('DEFAULT', 'debug')
    False
"""

from .. import parser, IniConfigFile
from insights.specs import Specs


@parser(Specs.ceilometer_conf)
class CeilometerConf(IniConfigFile):
    """
    A dict of the content of the ``ceilometer.conf`` configuration file.

    Example selection of dictionary contents::

        {
            "DEFAULT": {
                "http_timeout":"600",
                "debug": "False"
             },
            "api": {
                "port":"8877",
            },
        }
    """
    pass
