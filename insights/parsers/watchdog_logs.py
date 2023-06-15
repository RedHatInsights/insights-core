"""
WatchDogLog - file ``/var/log/watchdog/*.std*``
===============================================
"""

from insights import LogFileOutput, parser
from insights.specs import Specs


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
