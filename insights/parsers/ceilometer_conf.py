#  Copyright 2019 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

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
