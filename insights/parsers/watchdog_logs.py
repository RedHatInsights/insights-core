"""
WatchDogLog - file ``/var/log/watchdog/*.std*``
===============================================
"""

from insights import LogFileOutput, parser
from insights.specs import Specs
from insights.util import deprecated


@parser(Specs.watchdog_logs)
class WatchDogLog(LogFileOutput):
    """
    .. warning::
        This parser is deprecated, please use
        :py:class:`insights.parsers.watchdog.WatchDogLog` instead.

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

    def __init__(self, *args, **kwargs):
        deprecated(WatchDogLog, "Please use the :class:`insights.parsers.watchdog.WatchDogLog` instead.", "3.8.0")
        super(WatchDogLog, self).__init__(*args, **kwargs)

    time_format = None
