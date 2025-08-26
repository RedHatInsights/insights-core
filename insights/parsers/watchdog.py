"""
Parsers for watchdog configuration
==================================

WatchDogConf - file ``/etc/watchdog.conf``
------------------------------------------
WatchDogLog - file ``/var/log/watchdog/*.std*``
-----------------------------------------------
"""

from insights import parser, Parser, SkipComponent, LogFileOutput
from insights.specs import Specs
from insights.parsers import split_kv_pairs


@parser(Specs.watchdog_conf)
class WatchDogConf(Parser, dict):
    """
    Parsing the `/etc/watchdog.conf` file. It stores the data in a dict.

    Sample content::

        # The retry-timeout and repair limit are used to handle errors in a
        # more robust manner. Errors must persist for longer than this to
        # action a repair or reboot, and if repair-maximum attempts are
        # made without the test passing a reboot is initiated anyway.

        retry-timeout          = 60
        repair-maximum         = 1
        realtime               = yes
        priority               = 1

    Examples:
        >>> 'retry-timeout' in watchdog_conf_obj
        True
        >>> 'test-timeout' in watchdog_conf_obj
        False
        >>> watchdog_conf_obj.get('retry-timeout')
        '60'
        >>> watchdog_conf_obj.get('realtime')
        'yes'
    """
    def parse_content(self, content):
        self.update(split_kv_pairs(content))
        if not self:
            raise SkipComponent('Not available data')


@parser(Specs.watchdog_logs)
class WatchDogLog(LogFileOutput):
    """
    Class for parsing ``/var/log/watchdog/*.std*`` files.

    Sample Input::

        DEBUG:root:0

        INFO:root:Executing: /usr/bin/sg_persist -n -i -k -d /dev/mapper/mpathb

        DEBUG:root:0   PR generation=0xc2, 4 registered reservation keys follow:
            0xfdfe0001
            0xfdfe0001
            0xfdfe0000
            0xfdfe0000


        DEBUG:root:key fdfe0001 registered with device /dev/mapper/mpathb
        INFO:root:Executing: /usr/bin/sg_turs /dev/mapper/mpathb

        DEBUG:root:0
    """

    time_format = None
